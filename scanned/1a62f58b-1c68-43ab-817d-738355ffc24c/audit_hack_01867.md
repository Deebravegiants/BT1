# [H] `persistedData` Race Where `snap_manageState.get` Returns`null`

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

Metamask Error:
```
Oops! Something went wrong.
Snap Error: 'Cannot read properties of null (reading 'addresses')'. Error Code: '-32603'
```

`snap.request(, {method: 'snap_manageState', params: {operation: 'get'}})` may return `null`. Snap state is only initialized on rpc request method `hello` via `addAddress()`.

This is the only method that checks if the retrieved state is `null`:


**snap/src/utils/fetchAddress.ts:L5-L20**
```solidity
export const addAddress = async (address:string) => {

    const persistedData = await snap.request({
        method: 'snap_manageState',
        params: { operation: 'get' },
    });

    if(persistedData == null){
        const data = {
            addresses: [address],
            popuptoggle: 0,
        };
        await snap.request({
            method: 'snap_manageState',
            params: { operation: 'update', newState:data },
        });
```


**snap/src/index.ts:L12-L21**
```solidity
export const onRpcRequest: OnRpcRequestHandler = async ({
  origin,
  request,
}) => {
  switch (request.method) {
    case "hello": {
      await addAddress(request.params.address || "0x0");
      await confirmAddress();
      break;
    }
```

If the state was never initialized or there was a race where `rpc-hello()` was not called first, then the snap may run into a null deref exception (here `rpc-togglepopup`):


**snap/src/utils/toggleHelper.ts:L2-L12**
```solidity
let persistedData = await snap.request({
    method: 'snap_manageState',
    params: { operation: 'get' },
});

let popuptoggle = notifcount;

const data = {
    addresses: persistedData.addresses,
    popuptoggle: popuptoggle,
};
```

#### Recommendation

Wrap `snap_manageState` with a function that always falls back to safe defaults if the snap state was never set. This also obsoleted the future need to check if `persistedData` is `null` as the new method ensures safe non-null defaults. 

This should also silence some of the type errors reported by tslint that warn that attributes of `persistentdata` are read while it might be null (see 5 ).
