### Title
Cross-Tenant Webhook Impersonation via Unbound `shop-domain` Header - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, while the `shop` identifier used to route and label the resulting data comes from an HTTP header that is never included in the signed content. This breaks the binding: `shop authenticated ≠ shop attributed to the payload`, allowing a party who can obtain one valid `(body, hmac)` pair for the app to relabel that payload as belonging to any other shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#hmac` and `#to_signable_string` derive the signature material only from `@raw_body`: [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are all read from HTTP headers that are outside the signed content: [2](#0-1) 

`Registry.process` only checks `Utils::HmacValidator.validate(request)` (body-vs-secret) before trusting `request.shop` and dispatching to the handler with that shop value: [3](#0-2) 

`HmacValidator.validate` computes the signature purely from `to_signable_string` (the raw body) and the app's single, shop-independent `Context.api_secret_key`: [4](#0-3) 

Because `api_secret_key` is shared across every shop that has installed the app (it is not per-shop), any party who installs the app on their own store (a normal, unprivileged action) receives a genuine webhook with a valid `(body, hmac)` pair signed under that same shared secret. That party can then replay the same body and HMAC to the app's webhook endpoint while substituting the `shopify-shop-domain` header for a different, victim shop. `HmacValidator.validate` still succeeds because the header is never part of `to_signable_string`, and `Registry.process` passes `request.shop` (the attacker-controlled header) straight into `WebhookMetadata` for the handler to act on.

This is the direct analog of the report's "missing user-provided randomness" bug class: an identity-relevant field (`shop`) is acted upon by the protected operation but is not covered by the integrity mechanism (`HMAC`) that is supposed to bind it — exactly the "shop authenticated versus shop attributed to session/data" break called out in scope.

### Impact Explanation
Any handler logic keyed off `WebhookMetadata#shop` (e.g., mandatory compliance topics `shop/redact`, `customers/redact`, `customers/data_request` registered via `Registry`) can be tricked into performing shop-B actions using shop-A-signed data, or vice versa — a cross-tenant confusion primitive achievable purely from a valid but relabeled webhook delivery. This matches the in-scope "cross-tenant access" Critical impact category, since the gem itself performs no binding between the cryptographically verified bytes and the shop identifier it hands to application code.

### Likelihood Explanation
Requires no `api_secret_key`, no access token, and no privileged account — only that the attacker be a normal user able to install the target app on their own store (or otherwise obtain one legitimate `(body, hmac)` pair for the app) and be able to POST to the app's public webhook endpoint with a modified `shop-domain` header. This is squarely within the "unprivileged internet user" threat model defined for this analysis.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) header values into the HMAC-verified signable content, or require the host application to cross-check `request.shop` against a known/expected installed-shop record before dispatch, and document this requirement explicitly. At minimum, `Registry.process` should not implicitly trust `request.shop` as authenticated data derived from HMAC validation, since the current API surface invites exactly that assumption.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com`; the app registers webhooks (e.g., `customers/redact`) via `Registry.register`.
2. Shopify delivers a legitimate webhook to the app's endpoint with body `B` and header `shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)` — this uses the app-wide `api_secret_key`, not anything unique to the attacker's shop.
3. Attacker captures `B` and `H` from their own delivered webhook (no secret needed — it's their own webhook).
4. Attacker crafts a new HTTP POST to the same webhook endpoint with the same body `B` and the same `shopify-hmac-sha256: H` header, but sets `shopify-shop-domain: victim-shop.myshopify.com`.
5. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `B` against `H` using `Context.api_secret_key` — validation passes.
6. `request.shop` returns `"victim-shop.myshopify.com"` (unauthenticated header value), and this is what the registered handler receives in `WebhookMetadata`, causing the app to act as though the payload originated from the victim shop. [5](#0-4) [6](#0-5)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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
