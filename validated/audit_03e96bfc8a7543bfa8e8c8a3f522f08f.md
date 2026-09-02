### Title
Webhook `X-Shopify-Shop-Domain` and `X-Shopify-Topic` headers are trusted for tenant/topic identification without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` binds the HMAC verification to the raw request body only, while `#shop` and `#topic` are read directly from unauthenticated HTTP headers. `Registry.process` verifies the HMAC over the body, then uses the header-derived `shop` and `topic` to dispatch the payload to a handler and to tag the resulting `WebhookMetadata`. This is the same root-cause pattern as the reported bug: a value that is acted upon (here, tenant/topic identity) is not covered by the cryptographic/consistency check that gates the action (here, the HMAC), so the two can be desynchronized.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` and `Request#topic` are read from HTTP headers that are never mixed into the signable string: [2](#0-1) 

`HmacValidator.validate` computes `OpenSSL::HMAC.hexdigest` over `verifiable_query.to_signable_string` (i.e., the body) and compares it to the `hmac-sha256` header: [3](#0-2) 

`Registry.process` checks only this body HMAC, then trusts `request.topic` and `request.shop` (both header-derived, unverified) to select the handler and populate `WebhookMetadata`, which is handed to the app's business logic: [4](#0-3) 

The identity binding that should hold is: `shop used to authorize/scope the webhook action == shop that Shopify actually signed the delivery for`. Because the HMAC only covers `raw_body`, this equality is not enforced by the gem — `shop`/`topic` are "bytes parsed" but not "bytes verified," exactly the class of bug called out in the rules (a field acted on but not covered by the HMAC).

### Impact Explanation
Any principal capable of producing a genuinely Shopify-signed webhook body for one shop (e.g., an attacker who owns/controls a store installed on the same app, or who intercepts/replays a delivery) can present that same signed body to the app's webhook endpoint with an altered `X-Shopify-Shop-Domain` header. Since `HmacValidator.validate` never inspects headers, the forged request passes validation, and `WebhookMetadata#shop` is populated with the attacker-chosen shop rather than the shop Shopify actually generated/signed the payload for. Any app logic keyed off `WebhookMetadata.shop` (session lookup, per-tenant state changes, mandatory `shop/redact`/`customers/redact`/`customers/data_request` compliance actions, billing/entitlement changes, etc.) would then be applied to the wrong tenant — a cross-tenant integrity violation. This matches the "cross-tenant access" criterion in the Critical impact bucket, since the tenant boundary (`shop`) that gates which merchant's data/session the app acts on is not authenticated.

### Likelihood Explanation
Requires only the ability to send an HTTP POST with a header-modifiable `shop-domain`/`topic` value alongside a body+HMAC pair that was legitimately produced by Shopify for some shop using the app (e.g., the attacker's own installed store, or a captured delivery). No access to `api_secret_key`, access tokens, or privileged accounts is needed — only unprivileged control over request headers to the app's own webhook endpoint, satisfying the "unprivileged internet user" scope of this analysis.

### Recommendation
Bind `shop` (and ideally `topic`) into the HMAC-verified signable material, or otherwise cryptographically tie the header-derived identity to the verified body (e.g., include the shop domain in the signed payload contract expected from Shopify, or reject/ignore header values not corroborated by an independently verified source such as the session/access token used to fetch or acknowledge the webhook). At minimum, document and encourage host apps to cross-check `request.shop` against a known/authorized shop list before trusting `WebhookMetadata.shop` for tenant-scoped actions.

### Proof of Concept
1. App has two installed shops using the same client_secret: `shop-a.myshopify.com` (attacker-controlled) and `shop-b.myshopify.com` (victim).
2. Attacker triggers an event on `shop-a` causing Shopify to send a legitimately-signed webhook: body `B`, headers include `X-Shopify-Hmac-Sha256: HMAC(secret, B)`, `X-Shopify-Shop-Domain: shop-a.myshopify.com`, `X-Shopify-Topic: <topic>`.
3. Attacker replays this exact request to the app's webhook endpoint but rewrites `X-Shopify-Shop-Domain` to `shop-b.myshopify.com`.
4. `Request#hmac`/`#to_signable_string` only look at `hmac-sha256` header and `@raw_body` — both unchanged — so `HmacValidator.validate` in `Registry.process` (`lib/shopify_api/webhooks/registry.rb:190`) returns `true`.
5. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` with `shop == "shop-b.myshopify.com"` and dispatches to the handler, which now believes body `B` (attacker's own data/event) belongs to `shop-b`, even though Shopify never signed anything for `shop-b`. [4](#0-3)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

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
