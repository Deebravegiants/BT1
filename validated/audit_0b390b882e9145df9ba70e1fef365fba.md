### Title
Webhook shop identity is not bound by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC computed by `Utils::HmacValidator.validate` authenticates the body bytes but never binds the `shop-domain` header that is later used to identify the tenant. An unprivileged holder of one valid signed webhook (e.g., an attacker who installed the app on their own store and captured a legitimately delivered webhook) can replay the same body with a forged `x-shopify-shop-domain`/`shopify-shop-domain` header for a different shop, and the HMAC check still passes because the header is never part of the signed content.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 

only the `@raw_body` is included. `HmacValidator.validate_signature` computes the digest exclusively over `verifiable_query.to_signable_string`: [2](#0-1) 

`Registry.process` gates entirely on this HMAC check, then hands `request.shop` — parsed straight from the unauthenticated header — to the app's handler as the tenant identity: [3](#0-2) 

`Request#shop` simply reads the header with no cross-check against the signed bytes: [4](#0-3) 

The binding that should hold is `hmac(raw_body, api_secret_key) → (raw_body, shop)`, i.e. the shop the handler trusts should be cryptographically tied to the same signature that authenticates the payload. Instead the equality actually enforced is only `hmac(raw_body) == valid`, while `shop` is taken from an independent, unauthenticated field. Anyone who can obtain one validly-signed webhook body (trivially available to any merchant who installs the app on their own store, since Shopify signs webhooks per-body, not per-shop-header) can present that same body with a different `shop-domain` header value and have it accepted as if it originated from that other shop.

### Impact Explanation
This breaks the shop/tenant identity guarantee the library is supposed to provide to the handler: `Registry.process` raises `Errors::InvalidWebhookError` only when the HMAC over the body fails, never when the shop header disagrees with the shop that actually generated the payload. Host applications that trust `WebhookMetadata#shop` (as the library's own webhook handler contract instructs them to) will process data under the wrong tenant, i.e. cross-tenant access/confusion — one of the explicitly accepted High/Critical impact categories.

### Likelihood Explanation
Exploitation requires only capturing a single legitimately-signed webhook body (any merchant using the app can do this for their own shop, since the payload is not shop-specific) and resubmitting it directly to the app's public webhook endpoint with a different shop header — no access token, api_secret_key, or privileged account is needed. This is reachable purely by an unprivileged internet user who can install the app once.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) inside the HMAC-signed content, or otherwise cryptographically bind the `shop-domain` header to the payload before trusting it in `Registry.process`/`WebhookMetadata`. At minimum, document that `request.shop` is unauthenticated so host apps cannot rely on it as a tenant boundary without additional verification (e.g., checking it against a known list of shops that installed the app).

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com` and captures a real webhook delivery, e.g. body `{"id":1}` with header `x-shopify-hmac-sha256: <valid-for-body>` and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker POSTs the identical body and HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `Utils::HmacValidator.validate` succeeds because `to_signable_string` only checks `@raw_body`, which is unchanged. [5](#0-4) 
4. `Registry.process` invokes the handler with `shop: "victim.myshopify.com"`, so the host application performs the webhook's side effects (e.g., data sync, deletion, order processing) attributed to the victim tenant, even though the payload came from the attacker.

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
