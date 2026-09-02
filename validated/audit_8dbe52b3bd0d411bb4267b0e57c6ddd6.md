### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant shop spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` attribute used for tenant identification from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, but `Utils::HmacValidator.validate` only verifies the HMAC over the raw request **body**. The header is never part of the signed payload, so the `shop` identity handed to the webhook handler is unauthenticated even though the request as a whole is reported as HMAC-valid.

### Finding Description
`Webhooks::Registry.process` validates a webhook solely via: [1](#0-0) 

`Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string`: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns only the raw body — the `shop`, `topic`, `webhook_id`, and `api_version` accessors, which are all read straight from HTTP headers, are excluded from the signed content: [3](#0-2) 

Once the HMAC check passes, `Registry.process` builds `WebhookMetadata` directly from `request.shop` (the unauthenticated header) and dispatches it to the app's handler: [4](#0-3) 

The identity binding that should hold is: `shop authenticated by HMAC == shop used by the handler to attribute the webhook data`. Here the equality is broken: the HMAC only authenticates `(body)`, while the handler receives `(body, shop_header)` where `shop_header` is uncontrolled by the signature. This mirrors the report's underlying bug class — a system trusting a value that "changes" (here, the shop identity in the header) as if it were covered by the same integrity guarantee as the signed payload, when in fact it can be altered independently and out of sync with the authenticated data, i.e., an identity/state binding that isn't atomically enforced.

### Impact Explanation
An attacker who legitimately installs the target app on their own store (an unprivileged action requiring no leaked secrets) receives genuine Shopify webhooks addressed to that app, each with a valid HMAC computed over the body using the app's `client_secret` (known only to Shopify and the app, but the *signature itself* is delivered to the attacker as the receiver of their own webhook). The attacker can replay that exact `(body, hmac)` pair to the app's webhook endpoint while substituting an arbitrary victim shop domain in the `x-shopify-shop-domain` header. `HmacValidator.validate` still succeeds because it never inspected the header, and `Registry.process` forwards the forged `shop` to the app's handler as if Shopify had reported that data for the victim shop. Depending on how the host app's handler uses `WebhookMetadata#shop` (e.g., to look up a session, update per-shop state, or trigger shop-scoped side effects), this enables cross-tenant data confusion — an app could apply another store's webhook payload to a different store's account.

### Likelihood Explanation
This requires no privileged credentials, tokens, or TLS interception — only installing the app on an attacker-controlled store (a normal, unprivileged Shopify merchant action) and the ability to send arbitrary HTTP requests to the app's public webhook endpoint, which is by design internet-reachable. The gem itself provides no mitigation (no HMAC coverage of the shop header, no cross-check against a known/registered shop list), so the flaw is inherent to the library's `HmacValidator`/`Webhooks::Request` design rather than a host-application misuse.

### Recommendation
Include the shop domain (and other identity-bearing headers such as topic/webhook-id) in the HMAC-signable content used for webhook verification, or otherwise cryptographically bind the header values to the signed body before constructing `WebhookMetadata`. At minimum, document that `WebhookMetadata#shop` is unauthenticated and must be cross-validated by the host application against a known/installed-shop list before use.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`.
2. Shopify sends a genuine webhook to the app's endpoint with a valid `x-shopify-hmac-sha256` computed over the JSON body using the app's secret, and header `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker captures `(raw_body, hmac_header)` and replays them to the same endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Webhooks::Request.new(raw_body:, headers:)` exposes `shop` = `"victim-shop.myshopify.com"`; `HmacValidator.validate(request)` still returns `true` because `to_signable_string` only checks `raw_body`. [5](#0-4) 
5. `Registry.process` dispatches `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed_body, ...)` to the app's handler, which treats the attacker's own body as belonging to the victim shop.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```
