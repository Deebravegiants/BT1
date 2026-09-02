This confirms the finding. The `Webhooks::Request#to_signable_string` (line 36-38 in `lib/shopify_api/webhooks/request.rb`) is defined to return only `@raw_body`, meaning the HMAC computed by `HmacValidator.validate` (via `compute_signature(verifiable_query.to_signable_string, secret)`) is computed **exclusively over the raw request body**, never over the `shop-domain` header. Yet `request.shop` (parsed from that unauthenticated header) is passed straight into `WebhookMetadata` and handed to the app's webhook handler as the tenant identifier. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable string as only the raw HTTP body (`to_signable_string` returns `@raw_body`), while the `shop` attribute consumed downstream is parsed from the `x-shopify-shop-domain`/`shopify-shop-domain` header, which is never included in the HMAC-signed material. `Registry.process` validates only that the body hash matches the app's shared `client_secret` HMAC, then trusts the header-derived `shop` value unconditionally when constructing `WebhookMetadata` for the handler.

### Finding Description
The identity binding that should hold is: `hmac == HMAC(secret, body || shop)`, i.e. the shop the webhook is attributed to must be part of what's cryptographically verified. Instead the gem implements `hmac == HMAC(secret, body)` only: [5](#0-4) [2](#0-1) 

`Registry.process` raises only when the body-only HMAC fails, then immediately trusts `request.shop` (from the header) to build `WebhookMetadata` passed to the app's handler: [3](#0-2) 

Because every shop that installs the same app shares the same `client_secret`, any merchant/unprivileged internet user who has legitimately installed the app on their own store can trigger a webhook delivery with a body and HMAC that Shopify computed and signed for them, then relay that valid `(body, hmac)` pair to the app's webhook endpoint with the `shop-domain` header changed to an arbitrary victim shop. `HmacValidator.validate` will still pass because it never inspects the header, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the (attacker-supplied) body belongs to the victim shop.

### Impact Explanation
This breaks the equality `shop authenticated == shop the HMAC attests to`, resulting in cross-tenant data confusion: a handler that stores/updates per-shop state (e.g., updates a customer/order/product record keyed by `data.shop`) can be made to write attacker-controlled webhook payload content under a victim shop's tenant record, since this gem provides no protection binding the header-derived shop to the cryptographic signature.

### Likelihood Explanation
Exploitability only requires the attacker to control (or use) a store where the target app is installed — an "unprivileged internet user" scenario satisfying the audit's threat model — and to know the app's public webhook endpoint. No access token, `client_secret`, or privileged account is required; the request is a plain unauthenticated HTTP POST with a forged header.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) in the signable material actually verified, or otherwise ensure the header-derived `shop` is only trusted once cross-checked against session/tenant state already provisioned for that shop (e.g., verifying that the shop has, in fact, registered this webhook topic through this app installation), rather than trusting the raw header unconditionally after a body-only HMAC check.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`.
2. Attacker triggers a webhook event (e.g., updates a product) causing Shopify to POST a signed webhook: body `B`, header `x-shopify-hmac-sha256: HMAC(secret, B)`, header `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker intercepts/replays this request to the app's webhook endpoint but rewrites `x-shopify-shop-domain` to `victim.myshopify.com`. All other headers/body are untouched.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` and compares it to the header HMAC — this still matches because `B` is unchanged.
5. The handler receives `WebhookMetadata.new(topic:, shop: "victim.myshopify.com", body: B, ...)`, believing attacker-controlled body `B` is data belonging to `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
