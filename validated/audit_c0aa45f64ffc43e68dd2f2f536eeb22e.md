### Title
Webhook `shop` field is trusted for tenant identity without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only signs the raw HTTP body, while `ShopifyAPI::Webhooks::Registry.process` treats the unsigned `x-shopify-shop-domain` / `shopify-shop-domain` header as the authoritative tenant identifier passed to the host application's handler. Anyone in possession of one genuine webhook delivery (i.e. any merchant who has installed the app) can replay the same signed body while substituting a different shop domain header, causing the app to process/attribute the webhook as coming from an arbitrary victim shop.

### Finding Description
`HmacValidator.validate` computes and compares the HMAC only over `verifiable_query.to_signable_string`: [1](#0-0) 

For webhooks, `to_signable_string` is defined as just the raw body: [2](#0-1) 

`shop` however is read straight from an HTTP header that is not part of that signed string: [3](#0-2) 

`Registry.process` validates the HMAC (which only proves the body integrity), then forwards `request.shop` — the unauthenticated header — as the tenant identity to the host app's handler: [4](#0-3) 

The identity binding that should hold is:
`bytes_verified_by_HMAC == bytes_used_to_identify_the_tenant (shop)`

Here it is broken: `bytes_verified_by_HMAC == raw_body` while `bytes_used_to_identify_the_tenant == header["x-shopify-shop-domain"]`, and the latter is never included in the signed payload. Consequently a valid `(raw_body, hmac)` pair signed for shop A can be paired with a forged shop-domain header for shop B, and the signature will still validate, since `compute_signature` only re-hashes the raw body.

### Impact Explanation
This is a cross-tenant identity confusion: any existing merchant of the app (an unprivileged actor requiring no access to `client_secret` or any credential) can capture a legitimate webhook delivery sent to their own shop and replay it to the app's webhook endpoint with the `shop-domain` header changed to any other install's domain. Because `Registry.process` hands `request.shop` directly to the handler as the authenticated tenant, any host application that uses this field to select a merchant session, look up per-shop data, or otherwise scope tenant state will act on a request attributed to the wrong shop — a cross-tenant access vector, consistent with the "Critical – cross-tenant access" impact bucket.

### Likelihood Explanation
Likelihood is high given the low bar: no access token, API secret, or privileged account is needed — only a legitimate app installation on any shop (which any merchant can obtain by installing a public app) to capture one valid `(body, hmac)` pair, plus the ability to POST to the app's public webhook endpoint with a modified header. The gem does nothing to prevent this because the vulnerable binding is baked into `to_signable_string` and `Registry.process`.

### Recommendation
Bind the tenant identity into the signed material or otherwise cryptographically tie the `shop-domain` header to the HMAC before trusting it, e.g. include `shop`, `topic`, and `webhook_id` in `to_signable_string`, or independently validate that the shop the payload claims to be from matches an expected registration/session before dispatching to the handler.

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com`; Shopify delivers a webhook to the app with:
   - body `B`
   - headers: `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: H` (valid HMAC of `B` under the app's `client_secret`)
2. Attacker replays the exact same request to the app's webhook endpoint, changing only the header to `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (`= B`), matches `H`, and passes: [5](#0-4) 
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"`, even though the request never originated from Shopify on behalf of that shop, and the host app processes it as authentic data/event for the victim tenant.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
        end
```
