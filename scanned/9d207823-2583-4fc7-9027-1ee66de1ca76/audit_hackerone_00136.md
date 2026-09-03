# [H] Array Index Underflow--http rpc

## Summary
Severity: High
Program: Monero
Weakness: Array Index Underflow
Reporter: minerscan
State: resolved
Disclosed: 2021-10-11T20:35:12.885Z
Source: https://hackerone.com/reports/825091

## Details
## Summary:
parserse_base_utils.h:197
const unsigned char tmp = isx[(int)*++it];
Int type will cause the array subscript to appear negative and read wrong data, 
Solution:
const unsigned char tmp = isx[(unsigned char)*++it];

## Releases Affected:

  * up to date version on github
## Steps To Reproduce:
[add details for how we can reproduce the issue]

\#include <iostream>
\#include "serialization/keyvalue_serialization.h"
\#include "storages/portable_storage_template_helper.h"
\#include "storages/portable_storage_base.h"

\#ifdef __cplusplus
extern "C"
\#endif
int LLVMFuzzerTestOneInput(const char *data, size_t size) {
  std::string s(data,size);
  try
  {
    epee::serialization::portable_storage ps;
    ps.load_from_json(s);
  }
  catch (const std::exception &e)
  {
    std::cerr << "Failed to load from binary: " << e.what() << std::endl;
    return 1;
  }
  return 0;
}

## Supporting Material/References:


_Trimmed to 38 lines — full report: https://hackerone.com/reports/825091_
