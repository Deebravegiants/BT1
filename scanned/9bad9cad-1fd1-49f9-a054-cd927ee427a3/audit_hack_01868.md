# [M] TypeScript Errors

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

* `toggleHelper`

`persistedData` should be checked for `null` and default to a sane initial config. `notifcount:Number` should be `notifcount:number`.

```javascript
Type '{ addresses: Json; popuptoggle: Number; }' is not assignable to type 'Record<string, Json>'.
  Property 'popuptoggle' is incompatible with index signature.
    Type 'Number' is not assignable to type 'Json'.
      Type 'Number' is not assignable to type '{ [prop: string]: Json; }'.
        Index signature for type 'string' is missing in type 'Number'.ts(2322)
```


**snap/src/utils/toggleHelper.ts:L7-L16**
```solidity
let popuptoggle = notifcount;

const data = {
    addresses: persistedData.addresses,
    popuptoggle: popuptoggle,
};
await snap.request({
    method: 'snap_manageState',
    params: { operation: 'update', newState:data },
});
```

* `popupHelper`

`let msg = []` should be `let msg = [] as String[];`

```javascript
Variable 'msg' implicitly has an 'any[]' type.ts(7005)
```

* `addresses` can be `null`


**snap/src/utils/fetchnotifs.ts:L34-L37**
```solidity
export const fetchAllAddrNotifs = async () => {
    const addresses = await fetchAddress();
    let notifs:String[] = [];
    for(let i = 0; i < addresses.length; i++){
```


* `persistedData` can be `null`


**snap/src/index.ts:L63-L68**
```solidity
let persistedData = await snap.request({
  method: "snap_manageState",
  params: { operation: "get" },
});

let popuptoggle = Number(persistedData.popuptoggle) + msgs.length;
```

#### Recommendation

Fix the typescript configuration (see 1 ). Fix all reported ts-lint errors. Avoid using `any` types and use safe types instead.
