### Title
Shop-domain header used for tenant identity is not covered by the webhook HMAC, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook request's authenticity solely via `Utils::HmacValidator.validate`, which checks the HMAC over `Request#to_signable_string`. That method returns only the raw request body — it does not include the `x-shopify-shop-domain` (or `shopify-shop-domain`) header. Yet that same untrusted header is used as the tenant identifier (`request.shop`) passed straight into the handler as the authoritative shop for the webhook.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 
and `shop` is read directly from an HTTP header with no cross-check against the signed material: [2](#0-1) 

`Registry.process` only calls `Utils::HmacValidator.validate(request)` before dispatching to the handler with `request.shop` as the trusted tenant: [3](#0-2) 

`HmacValidator.validate` computes the HMAC using the app's single, shared `Context.api_secret_key` (the app's `client_secret`, identical for every shop that installs the app) over `verifiable_query.to_signable_string`, i.e., the raw body only: [4](#0-3) 

Compare this with `AuthQuery`, where `shop` **is** folded into the signed string via `to_signable_string`, correctly binding the shop identity to the signature: [5](#0-4) 

The equality that should hold is: `shop_bound_by_HMAC == shop_used_for_tenant_dispatch`. For `Request`, this equality is broken — `shop_bound_by_HMAC` is undefined (empty set, since shop is excluded from `to_signable_string`), while `shop_used_for_tenant_dispatch = request.shop`, an unauthenticated header value.

Because the HMAC secret (`api_secret_key`) is the app's single `client_secret`, shared across every shop that installs the same public/custom app, any unprivileged internet user can install the app on their own store (a merchant account they control) and receive a webhook whose body+HMAC pair is validly signed with that shared secret. They can then replay that exact `(body, hmac)` pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still passes (it only checks body bytes against the secret, not which shop sent it), and `Registry.process` forwards `shop: request.shop` (the forged victim domain) to the app's handler as if the payload legitimately originated from the victim.

### Impact Explanation
This crosses a tenant boundary: the receiving app is told an event happened for shop B (attacker-chosen) using data validly signed only under the app's shared secret, without shop B ever generating it. Depending on how the host app persists data or enqueues jobs (as `docs/usage/webhooks.md` recommends: `perform_later(topic: ..., shop_domain: data.shop, webhook: data.body)`), this enables cross-tenant data injection/corruption — e.g., faking `orders/create`, `app/uninstalled`, `customers/data_request`, or GDPR-mandatory topics for a shop the attacker does not control, using the trust boundary this gem itself establishes (`Registry.process` + `Request`) rather than any misuse of undocumented behavior.

### Likelihood Explanation
Any user can freely install a public Shopify app on their own development/test store, satisfying "unprivileged internet user" — no leaked credentials, TLS interception, or privileged account needed. Capturing one's own valid webhook `(raw_body, x-shopify-hmac-sha256)` pair and replaying it with a different `x-shopify-shop-domain` header is trivial with any HTTP client.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) header into the signed material, or otherwise cross-validate `request.shop` against a value independently established for that specific installation (e.g., verify a session/webhook subscription record keyed by shop exists and matches the topic/webhook id) before dispatching to handlers in `Registry.process`. At minimum, document that `data.shop` from `WebhookMetadata` must not be trusted as a strong tenant identifier without additional verification, since it is not covered by the HMAC.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`, completing OAuth normally (no special privilege required).
2. Attacker triggers a webhook subscribed by the app (e.g. `orders/create`) on their own store, capturing the raw POST body and the legitimate `x-shopify-hmac-sha256` header Shopify sends (both are valid because they're signed with the app's shared `client_secret`).
3. Attacker replays this captured `(raw_body, hmac header)` pair to the app's webhook endpoint but rewrites `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `hmac` against `raw_body` — the forged `shop` header is never included in that computation (`request.rb:35-38`, `hmac_validator.rb:26-31`).
5. The handler is invoked with `WebhookMetadata` whose `shop` is `"victim-shop.myshopify.com"` while `body` is fully attacker-controlled content, and the app processes/queues it as a legitimate victim-shop event.

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
