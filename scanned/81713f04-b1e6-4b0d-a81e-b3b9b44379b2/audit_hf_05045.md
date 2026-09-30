# [H] The worker and reputer's pay-

## Summary
Severity: High
Contest weight: 0.3741
Dataset id: 23049
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
InsertBulkWorkerPayload and InsertBulkReputerPayload does not check the ownership of the pubkey. As the result, the data from worker or reputer may be tampered.
Each worker signs their data and the elected lead node will send the bundle to the allora chain via InsertBulkWorkerPayload.
And the signature is check in the worker_data_bundle.Validate: It checks whether the InferenceForecastsBundle is signed by the private key from the given Pubkey. However, it was not checked whether the Pubkey belongs from the inferer, who is presumably signed the bundle. Without this check, an adversary may tamper with the data bundle and claim that the data is from an innocent inferer. The data will then recorded as the data from the inferer.
s/types/worker_data_bundle.go#L44-L56
The same issue exists in the msg_server_losses:InsertBulkReputerPayload. It is checked whether the ValueBundle was signed with the private for the Pubkey, but it was not checked that the key should belong to the reputer. Therefore, the value bundle may be tampered, but the data will recorded as the reputer's data.
s/types/reputer_value_bundle.go#L60-L71
The proof of work below demonstrates that the signature and the pubkey do not belong to the inferer:
// based on msg_server_worker_payload_test.go
func (s *MsgServerTestSuite) TestMsgInsertBulkWorkerPayloadPoC() {
ctx, msgServer := s.ctx, s.msgServer
require := s.Require()
workerPrivateKey := secp256k1.GenPrivKey()
adversary := secp256k1.GenPrivKey()
workerMsg, topicId := s.setUpMsgInsertBulkWorkerPayload(workerPrivateKey)
workerMsg = s.signMsgInsertBulkWorkerPayload(workerMsg, adversary)
blockHeight := workerMsg.WorkerDataBundles[0].InferenceForecastsBundle.Forecast.BlockHeight
forecastsCount0 := s.getCountForecastsAtBlock(topicId, blockHeight)
_, err := msgServer.InsertBulkWorkerPayload(ctx, &workerMsg)
require.NoError(err, "InsertBulkWorkerPayload should not return an error")
forecastsCount1 := s.getCountForecastsAtBlock(topicId, blockHeight)
require.Equal(forecastsCount0, 0)
require.Equal(forecastsCount1, 1)
}
The worker and reputer's data may be tampered and as the result, they may be punished or rewarded incorrectly.

## Recommendation
Consider adding the check for the ownership of the pubkey.
