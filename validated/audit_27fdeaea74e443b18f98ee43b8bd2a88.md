### Title
Webhook shop-domain and topic headers are trusted for tenant routing without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) and event `topic` from HTTP headers, but the HMAC signature that `Utils::HmacValidator` checks only covers the raw request body. `Registry.process` accepts any request whose body hash matches, then hands the (unauthenticated) `shop` header straight to the host application's handler as the trusted tenant identifier. This breaks the equality the library implicitly promises to callers: `shop-domain header == shop that produced/authorized the signed body`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` and `#topic` are read directly from headers, independent of the signed payload: [2](#0-1) 

`HmacValidator.validate` computes an HMAC-SHA256 over `verifiable_query.to_signable_string` (i.e., the raw body only) using `Context.api_secret_key`, and compares it to the `hmac` value taken from the `hmac-sha256` header — never touching `shop-domain` or `topic`: [3](#0-2) 

`Registry.process` only checks this body HMAC, then immediately trusts `request.shop` and `request.topic` to build the metadata passed to the app's handler: [4](#0-3) 

Because `api_secret_key` is a single per-app secret shared across every shop that installs the app, an attacker who owns/controls their own shop can install the app, receive a legitimately HMAC-signed webhook payload for their own shop (or otherwise obtain a validly-signed body via the same shared secret), then resend that same body to the app's webhook endpoint with a forged `X-Shopify-Shop-Domain` header pointing at a victim shop and/or a different `X-Shopify-Topic`. `HmacValidator.validate` still succeeds because the signature only covers the body, and `Registry.process` will invoke the registered handler with `WebhookMetadata` claiming the data belongs to the victim shop. Any host application that keys business logic, session lookups, or data writes off `data.shop` (as the docs instruct: `docs/usage/webhooks.md` and `WebhookMetadata`) will process attacker-supplied body content under the wrong tenant.

### Impact Explanation
This is a genuine cross-tenant identity-binding break: the field the library exposes as the authenticated tenant identifier (`shop`) is never bound to the cryptographic signature that is supposed to authenticate the request. A host app that trusts `WebhookMetadata#shop` (as the library's own documentation directs integrators to do) can be tricked into associating attacker-controlled webhook body content with a victim shop's tenant context, leading to cross-tenant data corruption/confusion without needing the victim's credentials. This matches the "Critical - cross-tenant access" impact category, since the shop binding that gates per-tenant processing is not actually enforced by the gem.

### Likelihood Explanation
Any unprivileged internet user who can install the target app on their own store (a normal, unprivileged action for public/installable apps) can obtain a validly HMAC-signed webhook body signed with the app's shared `api_secret_key`. Forging the `shop-domain`/`topic` headers on the replayed request requires no secret material at all, since those headers are not covered by the signature. The only prerequisite is that the host app's webhook endpoint is reachable and does not itself perform additional shop/topic binding (which the gem does not provide or document as necessary).

### Recommendation
Bind the `shop-domain` (and ideally `topic`, `api-version`, `webhook-id`) headers into the HMAC-verified signable string, or otherwise cryptographically bind them to the body (e.g., include them in the computed digest input) so `HmacValidator.validate` fails if any of these headers are tampered with relative to the signed payload. At minimum, document prominently that `request.shop`/`request.topic` are unauthenticated and must be independently cross-checked by the host application (e.g., against an expected/registered shop) before being trusted for tenant routing.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com`, obtaining webhook deliveries signed with the app's shared `api_secret_key`.
2. Attacker captures one such legitimate webhook POST: raw body `B`, with a valid `X-Shopify-Hmac-Sha256` header computed as `HMAC-SHA256(api_secret_key, B)`.
3. Attacker resends the exact same body `B` and the exact same `X-Shopify-Hmac-Sha256` header to the app's webhook endpoint, but replaces `X-Shopify-Shop-Domain` with `victim-shop.myshopify.com` (and optionally changes `X-Shopify-Topic`).
4. `ShopifyAPI::Utils::HmacValidator.validate` computes the HMAC only over `B` and succeeds, per `lib/shopify_api/utils/hmac_validator.rb:26-31`.
5. `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) invokes the app's handler with `WebhookMetadata` whose `shop` is `victim-shop.myshopify.com`, even though the body content actually originated from the attacker's own shop.

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
