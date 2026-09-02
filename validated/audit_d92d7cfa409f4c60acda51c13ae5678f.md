### Title
Webhook shop-domain header is not covered by HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw request body, while the `shop` (and `topic`/`webhook_id`) values are read from unauthenticated HTTP headers. `Utils::HmacValidator` only verifies the raw body against the HMAC, so the `shop` value that `Webhooks::Registry.process` hands to application webhook handlers is never bound to the HMAC-validated bytes. An attacker who owns any shop with the app installed can capture one legitimate, HMAC-valid webhook delivery for their own shop and replay it to the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to point at a victim shop, causing the app to process attacker-controlled webhook data under the victim's tenant identity.

### Finding Description
The identity binding that should hold is:

`shop value trusted by the handler == shop value cryptographically bound to the HMAC-signed bytes`

This does not hold in the gem:

- `Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

- `Request#shop` is read straight from an attacker-controllable HTTP header, with no cryptographic tie to the body/HMAC: [2](#0-1) 

- `HmacValidator.validate_signature` computes the signature purely over `verifiable_query.to_signable_string` (i.e., the raw body) and compares it to the received HMAC — it never incorporates `shop`, `topic`, or `webhook_id`: [3](#0-2) 

- `Registry.process` validates only the body/HMAC pairing, then immediately trusts `request.shop` (from the header) to build the `WebhookMetadata` passed to the app's handler — the exact value used by apps to key their tenant data: [4](#0-3) 

Because the HMAC only binds the body, and `shop` is sourced independently from a header, any request with a *previously valid* `(raw_body, hmac)` pair — regardless of which shop it originally belonged to — will pass `HmacValidator.validate` no matter what `shop` header is attached to it. The gem's own tests demonstrate this decoupling: the webhook test fixtures compute the HMAC solely from the JSON body and shop is set independently in the headers hash, confirming the shop is never part of the signed material. [5](#0-4) 

### Impact Explanation
This is a cross-tenant access vector (Critical). A user of the app on Shop A (attacker) can trigger a webhook on their own shop (e.g., a product/order update) and capture the resulting valid `(raw_body, x-shopify-hmac-sha256)` pair — this requires no secrets, since the attacker legitimately receives their own shop's webhooks. They then POST the identical body/HMAC to the app's public webhook endpoint with `x-shopify-shop-domain` swapped to Shop B (the victim). `HmacValidator.validate` succeeds because it only checks the body, and `Registry.process` passes `shop: "victim-shop.myshopify.com"` to the app's handler alongside attacker-chosen body content. Any app that (as intended and documented) uses `WebhookMetadata#shop` to select which tenant's data/session to update will write or act on the attacker's payload under the victim's tenant, achieving cross-tenant data corruption/injection without needing the victim's or the app's credentials.

### Likelihood Explanation
Likelihood is high for any multi-tenant app built on this gem: exploitation only requires the attacker to be a legitimate installer of the app on any shop (an "unprivileged internet user" relative to other tenants), the ability to receive one webhook for their own store, and the ability to send an arbitrary HTTP POST to the app's public webhook endpoint with custom headers — no access to the app's `api_secret_key` or any other tenant's credentials is needed.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the material that is HMAC-verified, or otherwise cryptographically tie the header-derived shop to the signed body before it is exposed to handlers:
- Have `Request#to_signable_string` include the `shop`, `topic`, and `webhook_id` header values concatenated with the raw body (in a canonical, unambiguous encoding) instead of the raw body alone, and update `HmacValidator` accordingly, or
- If Shopify's webhook signature scheme fundamentally only covers the raw body (matching the actual `X-Shopify-Hmac-SHA256` header semantics), document loudly that `shop`/`topic`/`webhook_id` headers are **not** authenticated by the HMAC and must not be trusted for tenant routing without an independent verification step (e.g., cross-checking against a shop-scoped webhook registration/subscription id fetched via the Admin API), and consider rejecting/flagging requests where the header shop does not match an expected shop for the given webhook subscription id.

### Proof of Concept
1. Install the app on attacker-controlled `attacker-shop.myshopify.com`; trigger any subscribed webhook topic (e.g., `orders/create`) and capture the raw POST body plus the `x-shopify-hmac-sha256` header Shopify sent.
2. Replay this exact `(raw_body, x-shopify-hmac-sha256)` pair to the app's webhook endpoint, but set `x-shopify-shop-domain: victim-shop.myshopify.com` and `x-shopify-topic`/`x-shopify-webhook-id` to any desired values.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `raw_body` against the HMAC: [6](#0-5) 
4. The handler receives `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body: <attacker-controlled parsed body>, ...)`, and any app logic keying storage/session updates off `shop` will apply the attacker's webhook payload to the victim shop's tenant data.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** test/webhooks/registry_test.rb (L16-30)
```ruby
        hmac = OpenSSL::HMAC.digest(
          OpenSSL::Digest.new("sha256"),
          ShopifyAPI::Context.api_secret_key,
          "{}",
        )

        @headers = {
          "x-shopify-topic" => @topic,
          "x-shopify-hmac-sha256" => Base64.encode64(hmac),
          "x-shopify-shop-domain" => @shop,
          "x-shopify-webhook-id" => "b1234-eefd-4c9e-9520-049845a02082",
          "x-shopify-api-version" => "2024-01",
        }

        @webhook_request = ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: @headers)
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-190)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
```
