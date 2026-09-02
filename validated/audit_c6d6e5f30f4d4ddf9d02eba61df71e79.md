Confirmed: `Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `api_version`, and `webhook_id` are read straight from HTTP headers that are excluded from the signed payload [2](#0-1) . `Registry.process` validates only that HMAC and then forwards `request.shop` as the trusted tenant identity to the handler [3](#0-2) .

### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` signs only the raw JSON body of an incoming webhook request. The `shop-domain`, `topic`, `api_version`, and `webhook-id` values are read directly from HTTP headers and are never included in the HMAC-signed material. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC over the body only, then unconditionally trusts `request.shop` (taken from the unauthenticated `X-Shopify-Shop-Domain` header) as the tenant identity passed to the app's handler.

### Finding Description
The identity binding that should hold is: `shop-domain (header, trusted by handler)` == `shop that the HMAC-signed body actually originates from`. In this gem that binding is never enforced.

- `HmacValidator.validate` computes the signature only over `verifiable_query.to_signable_string` [4](#0-3) .
- For webhook requests, `to_signable_string` is hard-coded to `@raw_body` [1](#0-0) , so the `shop`, `topic`, `webhook_id`, and `api_version` headers are completely outside the signed data.
- `Registry.process` raises only if the body HMAC is invalid, then builds `WebhookMetadata` using `request.shop` straight from the header, and dispatches it to the registered handler as the authoritative tenant identity [3](#0-2) .

Because the `api_secret_key` used to compute the webhook HMAC is shared by the app across every shop that installs it (it is not a per-shop secret — see the same key used in `HmacValidator.validate_signature` for all installs, `lib/shopify_api/utils/hmac_validator.rb:26-31`), a valid `(raw_body, hmac)` pair obtained from one real, legitimately-delivered webhook is valid for that raw body regardless of which shop it was delivered to. Any unprivileged internet user can freely install a public/development app on their own store, trigger an event to have Shopify deliver a real webhook with a valid HMAC to the app's endpoint, capture that exact `(raw_body, hmac)` pair, and then replay it directly to the app's webhook endpoint while swapping only the `X-Shopify-Shop-Domain` header (and, if desired, `X-Shopify-Webhook-Id`/`X-Shopify-Topic`, which are equally unauthenticated) to claim it originated from a different, victim shop. `Registry.process` will accept it, because it only re-verifies the (unchanged) body HMAC, and will hand the spoofed shop identity to the app's handler as trusted `WebhookMetadata#shop`.

### Impact Explanation
This breaks the tenant/shop identity binding relied upon by any app handler that uses `WebhookMetadata#shop` to key into per-shop data (e.g., to look up the shop's session/access token, or to write/update per-shop records). An attacker-controlled shop can inject webhook payloads that the host application will process and attribute to an arbitrary victim shop, achieving cross-tenant access/data corruption in any application built on this gem's documented webhook API — satisfying the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high for any app using `ShopifyAPI::Webhooks::Registry`/`Request` as documented: the attacker needs no privileged credentials, no access to `api_secret_key`, and no MITM — only their own (free/trial) shop installation of the target app, from which they can legitimately receive at least one real webhook and replay it with a modified header to the same public webhook endpoint.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the HMAC-signed material for webhook requests (or otherwise cryptographically bind the shop-domain header to the signed body), and reject requests where the declared header values are not verifiably tied to the signed payload. At minimum, document that `WebhookMetadata#shop` must not be trusted as an authenticated tenant identifier unless the host application independently correlates it (e.g., against a known/installed shop list) before using it as a data-access key.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and triggers a real event so Shopify delivers a legitimate webhook: headers `X-Shopify-Hmac-Sha256: <H>`, `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Topic: orders/create`, body `B`.
2. Attacker computes/observes that `H = HMAC-SHA256(api_secret_key, B)` — note this does not depend on the shop-domain header at all, per `to_signable_string` [1](#0-0) .
3. Attacker resends the exact same body `B` and HMAC `H` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `B` against `H` [5](#0-4) .
5. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ..., ...)` and processes/stores attacker-controlled data under the victim shop's identity [6](#0-5) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
