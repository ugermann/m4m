#!/bin/bash

dir=${1:-.}
find $dir -name '*.multi-bleu' \
| xargs grep BLEU \
| perl -pe 's!.*?([^/]+)/systems/!$1:!;s!/eval.*/([0-9]+)/.*BLEU =! [$1]!;' \
| sort -k3 -rg
