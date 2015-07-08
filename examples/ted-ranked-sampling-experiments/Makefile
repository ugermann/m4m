# -*- mode: makefile-gmake; tab-width: 4; -*-

# toolchain: 
fast_align.executable = /fs/snotra0/germann/code/fast_align/bin/runtime/fast_align

# translation system configuration

L1 = $(shell basename `pwd` | sed 's/-.*//')
L2 = $(shell basename `pwd` | sed 's/.*-//')

# $(info L1=${L1} L2=${L2})

# model setup
waln.method = fast
waln.maxlen = 120

variant ?= ranked
ifeq ($(variant),ranked)
sapt.cumb ?= 0
MOSES_ROOT = /fs/sif0/germann/moses/ranked-sampling-v.0.1.0c
else
ifeq ($(variant),random)
MOSES_ROOT = /fs/sif0/germann/moses/mmt-mvp-v0.2.1
else
$(error variant must be ranked or random)
endif
endif


lm ?= ted,ep7
tm ?= ep7+ted
sapt.sample=1000
PWD = $(shell cd . && pwd)
PREFIX  := $(CURDIR)/lm.$(lm).tm.$(tm).$(shell printf '%04d' ${sapt.sample})/$(variant)$(addprefix .cumb.,${sapt.cumb})
TM_PATH  = $(PWD)/mdl
LM_PATH  = $(TM_PATH)

corpusname ?= $(tm)
pllshards ?= $(sort $(subst +, ,$(subst $(,), ,$(tm))))
SKIP_MODULES = mgiza
include ../m4m/modules/m4m.m4m

$(info lm $(lm))
$(info tm $(tm))
$(info pll $(pllshards))
$(info mno $(mnoshards))

define select_lm_training_data

$$(info GOT $1)
lm.training-data := $(addprefix $(MNO_TOK)/$(cs2)/,$(filter $1,$(mnoshards)))
lm.training-data += $(addprefix $(PLL_TOK)/$(cs2)/,$(filter-out $(mnoshards),$1))
lm.training-data := $$(addsuffix .${L2}$(zipped),$$(lm.training-data))

endef

,:=,
$(foreach combo,$(subst $(,), ,$(lm)),$(info LM COPONENT: $(combo));\
$(eval $(call select_lm_training_data,$(subst +, ,${combo})));\
$(eval lm.corpusname=${combo});$(eval $(add_kenlm)))
$(eval $(call add_sapt,$(tm),$(PLL_CLN),$(PLL_ALN)/$(waln.method),$(TM_PATH)))
$(eval $(call create_moses_ini,${PREFIX}))

$(DEV_TOK)/$(cs1)/dev%.${L1}: | $(DEV_TOK)/$(cs1)/dev%.lst 
$(DEV_TOK)/$(cs1)/dev%.${L2}: devfiles
	$(lock)
	cat ${@D}/*.dev$*.*${L2} > $@_ && mv $@_ $@
	$(unlock)

$(DEV_TOK)/$(cs1)/%.lst: devfiles
	$(lock)
	for f in ${@D}/*.$*.*${L1}; do basename $$f; done >> $@_ && mv $@_ $@
	$(unlock)

$(TST_TOK)/$(cs1)/tst%.${L1}: | $(TST_TOK)/$(cs1)/tst%.lst 
$(TST_TOK)/$(cs1)/tst%.${L2}: tstfiles
	$(lock)
	cat ${@D}/*.tst$*.*${L2} > $@_ && mv $@_ $@
	$(unlock)

$(TST_TOK)/$(cs1)/%.lst: tstfiles
	$(lock)
	for f in ${@D}/*.$*.*${L1}; do basename $$f; done >> $@_ && mv $@_ $@
	$(unlock)

.PHONY: 
devfiles: | $(addprefix $(DEV_TOK)/$(cs1)/,$(addsuffix .${L1},$(devshards)))
devfiles: | $(addprefix $(DEV_TOK)/$(cs2)/,$(addsuffix .${L2},$(devshards)))
tstfiles: | $(addprefix $(TST_TOK)/$(cs1)/,$(addsuffix .${L1},$(tstshards)))
tstfiles: | $(addprefix $(TST_TOK)/$(cs2)/,$(addsuffix .${L2},$(tstshards)))

devset: $(foreach y,2010 2014,$(DEV_TOK)/$(cs1)/dev$y.lst)
devset:	$(foreach y,2010 2014,$(addprefix $(DEV_TOK)/$(cs1)/dev$y.,${L2}))

evalset: tstfiles
evalset: | $(foreach y,10 11 12,$(TST_TOK)/$(cs1)/tst20$y.lst)
evalset: | $(foreach y,10 11 12,$(addprefix $(TST_TOK)/$(cs1)/tst20$y.,${L2}))

system: $(PREFIX)/moses.ini.0
	$(info SYSTEM IS $<)

#eval.docs ?= tst2010 tst2011 tst2012
eval.docs ?= tst2010 
eval.sets  = $(addprefix $(TST_TOK)/$(cs1)/,$(eval.docs))
eval.sets  = $(addprefix $(TST_TOK)/$(cs1)/,$(eval.docs))
tune.docs ?= dev2010
tune.sets  = $(addprefix $(DEV_TOK)/$(cs1)/,$(tune.docs))
tune.run   = 1
tune.runs  = $(shell seq `echo ${tune.run} | perl -pe 's/^([0-9]+)$$/\1 \1/;s/-/ /;'`)

tuned.ini   = ${PREFIX}/tuned/$(notdir ${tuneset})/${run}/moses.ini
eval        = ${PREFIX}/eval/$(notdir ${tuneset})/${run}/$(notdir ${evalset})


realmoses := $(moses)
mert.decoder-flags += --filelist $(abspath ${tune.lst})
mert.decoder-flags += --moses $(realmoses)

eval.decoder-flags += --filelist $(abspath ${eval.lst})
eval.decoder-flags += --moses $(realmoses)

ifeq ($(variant),ranked)
mert.decoder-flags += --context-window all 
eval.decoder-flags += --context-window all 
$(info MERT: $(mert.decoder-flags))
$(info EVAL: $(eval.decoder-flags))
else 
$(info NO RANKING)
endif

moses := $(abspath $(m4mdir)/scripts/moses.doc4doc.py)

$(foreach tuneset,${tune.sets},\
$(foreach run,$(subst ${comma},${space},${tune.runs}),\
$(eval $(call tune_system,${PREFIX}/moses.ini.0,${tuned.ini},${tuneset}.lst));\
$(foreach evalset,$(eval.sets),\
$(eval $(call bleu_eval,${eval},${tuned.ini},${evalset}.lst)))))

tm: ${MOSES_INI_PREREQ}

info:
	$(info PTABLE_ENTRIES $(PTABLE_ENTRIES))
	$(info LMODELS: ${LMODELS})
	$(foreach l,$(LMODELS),$(info LMODEL: $l))
	$(foreach t,$(TUNED_SYSTEMS),$(info TUNED SYSTEM: $t))
	$(foreach e,${EVALUATIONS},$(info EVALUATIONS: $e))

tune: ${TUNED_SYSTEMS}
eval: ${EVALUATIONS}
.PHONY: nil eval
nil:
	echo done