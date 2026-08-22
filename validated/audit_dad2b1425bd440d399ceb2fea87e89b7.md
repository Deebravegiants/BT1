### Title
Local biometric images deleted after upload attempt regardless of upload success/failure - ([File: src/agents/image_uploader.rs])

### Summary
`orb-core`'s image-uploader agent mirrors the "burn-before-confirm" bug class described in the external report: it destroys the only local copy of a user's biometric capture data after attempting to upload it to the backend, without verifying that every individual upload actually succeeded. A network failure, an expired/invalid presigned URL, or an S3-side rejection during upload silently continues the loop and is still followed by an unconditional deletion of the local image directory, permanently losing the biometric data on both the device and (if the specific upload failed) the backend.

### Finding Description
In `upload_saved_images`, each image upload is attempted via `upload_image`, but `upload_image` never propagates upload failures as an `Err` — it only logs and increments a Datadog counter on failure and always returns `Ok(())`: [1](#0-0) 

Because failures are swallowed, the calling loop in `upload_saved_images` proceeds to the next image regardless of whether the previous `PUT` to the presigned S3 URL succeeded, and after the loop finishes it unconditionally deletes the entire image directory from local SSD storage: [2](#0-1) 

The same unconditional-deletion pattern repeats one level up in `upload_signup_images`, which removes the whole signup directory (containing IR/RGB/thermal/identification images) after calling `upload_saved_images` for each image category and `upload_identification_images_impl` for the self-custody candidate images, again with no check that every sub-upload actually succeeded: [3](#0-2) 

The actual network request performed for each image is a simple `PUT` to a presigned S3 URL that can fail for many benign reasons (expired URL, network drop, backend outage, S3 error): [4](#0-3) 

This is structurally the same root cause as the reported `BurnUnlock` issue: an irreversible local "burn" (deleting the only local copy of the data) is performed without confirming that the remote "mint"/persist step actually completed successfully. There is no retry queue, no persisted set of "images not yet confirmed uploaded," and no re-attempt mechanism — once `remove_dir_all` runs, the data is gone from the device, and if the specific `PUT` failed, it never reached the backend either.

### Impact Explanation
Biometric capture images (IR, RGB, thermal, and identification/self-custody images) are used by the backend for signup verification, fraud review, and self-custody key derivation workflows. If the upload silently fails for one or more images but the directory is deleted anyway, that biometric data is unrecoverable: it does not exist on the backend (upload failed) and no longer exists on the orb (directory removed). This can break downstream flows that depend on having a complete image set (e.g., fraud investigation, self-custody package validation) and results in a permanent, irreversible loss of user biometric data with no mechanism for detection or recovery — analogous to the token loss described in the source report, but manifesting as data loss rather than financial loss.

### Likelihood Explanation
This agent runs automatically during idle periods (and during fraud detection) whenever cached signup images exist on the SSD, per the module's own documentation: [5](#0-4) 
Any transient network failure, an expired presigned URL (URLs are requested per-image right before upload, so timing/latency issues are plausible), or a backend/S3-side error during the upload window is sufficient to trigger data loss — this does not require an attacker or privileged access, only normal operational conditions (poor connectivity, backend downtime) that are common for field-deployed hardware.

### Recommendation
Track per-image (and per-directory) upload success explicitly, and only delete local files/directories once every upload in that batch is confirmed successful. On failure, retain the files for a later retry attempt rather than deleting them. Concretely:
- Change `upload_image` to propagate upload errors instead of swallowing them and returning `Ok(())`.
- In `upload_saved_images`, only call `fs::remove_dir_all(image_dir)` after confirming all uploads in `paths` succeeded (e.g., accumulate a success flag or bail out early on the first failure and skip deletion).
- In `upload_signup_images`, only remove `signup_dir` after `upload_saved_images` and `upload_identification_images_impl` all return success, and leave partially-uploaded signup data intact for retry on the next `upload_all_signup_images` pass.

### Proof of Concept
1. A signup completes and images are cached under `DATA_ACQUISITION_BASE_DIR/<signup_id>/...` by `image_notary`.
2. The image-uploader agent starts uploading via `upload_all_signup_images` → `upload_signup_images` → `upload_saved_images`.
3. During upload of one image, the presigned URL request or the S3 `PUT` fails (e.g., transient network blip) — `upload_image::request` returns `Err`, which `upload_image` (in `image_uploader.rs`) catches, logs, and converts to `Ok(())`. [6](#0-5) 
4. The loop in `upload_saved_images` continues to the next image and, once done, unconditionally calls `fs::remove_dir_all(image_dir)`. [7](#0-6) 
5. The failed image no longer exists locally and was never received by the backend — it is permanently lost, with only a Datadog error counter (`main.count.data_acquisition.upload.error...`) as evidence anything went wrong.

### Citations

**File:** src/agents/image_uploader.rs (L79-82)
```rust
/// NOTE: This agent is not thread-safe and it might create race conditions if
/// it used from multiple places simultaneously. Currently we use this agent
/// only in 2 places. During idle state, and during fraud detection. Both these
/// Orb states are mutually exclusive with respect to execution.
```

**File:** src/agents/image_uploader.rs (L127-145)
```rust
    for path in paths {
        let image_id = ImageId::from_image_path(&path)?;
        let img_data = ssd::perform_async(async { fs::read(&path).await }).await;
        let Some(img_data) = img_data else {
            continue;
        };
        upload_image(
            signup_id,
            &image_id,
            presigned_url_type,
            img_data,
            &path.display().to_string(),
            image_dir_name,
        )
        .await?;
    }
    ssd::perform_async(async { fs::remove_dir_all(image_dir).await }).await;
    Ok(())
}
```

**File:** src/agents/image_uploader.rs (L147-171)
```rust
async fn upload_image(
    signup_id: &SignupId,
    image_id: &ImageId,
    presigned_url_type: UrlType,
    img_data: Vec<u8>,
    log_image_path: &str,
    dd_image_tag: &str,
) -> Result<()> {
    tracing::info!("Uploading image: {log_image_path}");
    let t = Instant::now();
    let response =
        upload_image::request(signup_id, image_id, presigned_url_type, img_data, dd_image_tag)
            .await;
    dd_timing!("main.time.data_acquisition.upload" + format!("{}.full", dd_image_tag), t);
    match response {
        Ok(()) => {
            dd_incr!("main.count.data_acquisition.upload.success" + format!("{}", dd_image_tag));
        }
        Err(e) => {
            dd_incr!("main.count.data_acquisition.upload.error" + format!("{}", dd_image_tag));
            tracing::error!("Uploading image {log_image_path} failed: {e}");
        }
    }
    Ok(())
}
```

**File:** src/agents/image_uploader.rs (L173-192)
```rust
async fn upload_signup_images(signup_dir: &Path) -> Result<()> {
    // extract last element of signup directory path as String
    let signup_id = SignupId::from_signup_dir(signup_dir)?;
    let t0 = Instant::now();
    upload_saved_images(signup_dir, "ir_camera", &signup_id, UrlType::Ir).await?;
    dd_timing!("main.time.data_acquisition.upload.batch.ir_camera", t0);
    let t1 = Instant::now();
    upload_saved_images(signup_dir, "rgb_camera", &signup_id, UrlType::Rgb).await?;
    dd_timing!("main.time.data_acquisition.upload.batch.rgb_camera", t1);
    let t2 = Instant::now();
    upload_saved_images(signup_dir, "ir_face", &signup_id, UrlType::IrFace).await?;
    dd_timing!("main.time.data_acquisition.upload.batch.ir_face", t2);
    let t3 = Instant::now();
    upload_saved_images(signup_dir, "thermal", &signup_id, UrlType::Thermal).await?;
    dd_timing!("main.time.data_acquisition.upload.batch.thermal", t3);
    upload_identification_images_impl(signup_id).await?;
    dd_timing!("main.time.data_acquisition.upload.batch.full_signup", t0);
    ssd::perform_async(async { fs::remove_dir_all(signup_dir).await }).await;
    Ok(())
}
```

**File:** src/backend/upload_image.rs (L16-36)
```rust
pub async fn request(
    signup_id: &SignupId,
    image_id: &ImageId,
    presigned_url_type: UrlType,
    img_data: Vec<u8>,
    dd_image_type: &str,
) -> Result<()> {
    let t: Instant = Instant::now();
    let presigned_url::Response { url: presigned_url, .. } =
        presigned_url::request(&DATA_BACKEND_URL, signup_id, Some(image_id), presigned_url_type)
            .await?;
    dd_timing!("main.time.data_acquisition.upload" + format!("{}.presigned", dd_image_type), t);
    tracing::debug!("Image presigned_url: {:?}", presigned_url);
    let request =
        super::client()?.put(presigned_url).header(CONTENT_LENGTH, img_data.len()).body(img_data);
    let t = Instant::now();
    let response = request.send().await?;
    dd_timing!("main.time.data_acquisition.upload" + format!("{}.upload", dd_image_type), t);
    response.error_for_status()?;
    Ok(())
}
```
