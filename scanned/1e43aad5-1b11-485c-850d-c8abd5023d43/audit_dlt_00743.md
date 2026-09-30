# [?] fix(ci): Prevent race condition in GCP static IP assignment (#10159)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-01-26
Source: https://github.com/ZcashFoundation/zebra/commit/650d0f25cfcf54200e1ce2d5c8e945025a68951f
Type: security-commit

## Details
fix(ci): Prevent race condition in GCP static IP assignment (#10159)

Use --no-address in instance template so instances start without
ephemeral IPs. This prevents the MIG controller from racing to restore
ephemeral IPs when assigning static IPs.

Closes #10158

## Patch
### .github/workflows/zfnd-deploy-nodes-gcp.yml
```diff
@@ -340,6 +340,7 @@ jobs:
           --image-project=cos-cloud \
           --image-family=cos-stable \
           --subnet=${{ vars.GCP_SUBNETWORK }} \
+          --no-address `# Static IPs are assigned after MIG creation; avoids race conditions` \
           --create-disk="${DISK_PARAMS}" \
           --container-mount-disk=mount-path='/home/zebra/.cache/zebra',name=${DISK_NAME},mode=rw \
           --container-stdin \
@@ -454,6 +455,8 @@ jobs:
           IFS=$'\n' read -rd '' -a INSTANCE_ROWS <<<"$INSTANCE_DATA" || true
 
           # Loop to assign all IPs
+          # Note: Instance template uses --no-address, so instances start without external IP.
+          # This avoids race conditions with MIG trying to restore ephemeral IPs.
           for i in "${!INSTANCE_ROWS[@]}"; do
             [ -z "${IP_ADDRESSES[$i]}" ] && continue
 
@@ -462,19 +465,17 @@ jobs:
 
             echo "Assigning ${IP_ADDRESS} to ${INSTANCE_NAME} in zone ${ZONE}"
 
-            gcloud compute instances delete-access-config "${INSTANCE_NAME}" \
-              --access-config-name="external-nat" \
-              --zone="${ZONE}" || true
+            # First: Configure stateful IP policy (tells MIG to preserve this IP)
+            gcloud compute instance-groups managed update-instances "${MIG_NAME}" \
+              --instances="${INSTANCE_NAME}" \
+              --stateful-external-ip "interface-name=nic0,address=${IP_ADDRESS},auto-delete=never" \
+              --region "${{ vars.GCP_REGION }}"
 
+            # Then: Add the static IP access config to the instance
             gcloud compute instances add-access-config "${INSTANCE_NAME}" \
               --access-config-name="external-nat" \
               --address="${IP_ADDRESS}" \
               --zone="${ZONE}"
-
-            gcloud compute instance-groups managed update-instances "${MIG_NAME}" \
-              --instances="${INSTANCE_NAME}" \
-              --stateful-external-ip "interface-name=nic0,address=${IP_ADDRESS},auto-delete=never" \
-              --region "${{ vars.GCP_REGION }}"
           done
 
       # Detect how many zones the MIG spans (needed for max-unavailable constraint)
```
