This confirms a clear asymmetry within the gem's own design: for OAuth (`AuthQuery#to_signable_string`), the `shop` field IS included inside the HMAC-signed string, so the shop identity is cryptographically bound to the signature. But for webhooks (`Request#to_signable_string`), only `@raw_body` is signed — `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from unauthenticated HTTP headers and are never part of the HMAC input.

### Title
Webhook shop/topic/webhook_id identity fields are not covered by HMAC verification, enabling cross-tenant webhook forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are parsed directly from attacker-controllable HTTP headers [2](#0-1) . `Utils::HmacValidator.validate` only checks that the HMAC matches `to_signable_string`, i.e. the body, using the app's shared `client_secret` [3](#0-2) . `Registry.process` then trusts these unauthenticated header fields directly to dispatch the handler and build `WebhookMetadata` [4](#0-3) .

### Finding Description
The identity binding broken is: **shop authenticated by the HMAC** (which only covers the raw body, keyed by the app's single shared `client_secret` for all installed shops) **≠ shop passed to the merchant's webhook handler** (`request.shop`, read from the `x-shopify-shop-domain`/`shopify-shop-domain` header, entirely outside the signed payload). The same applies to `topic` and `webhook_id`.

Because the app's webhook secret (`client_secret`) is shared across every shop that installs the app (it is not shop-specific), any shop that has legitimately installed the app receives genuine webhook deliveries with a valid body+HMAC pair for its own tenant. That attacker-controlled merchant can then replay the exact same `raw_body`/HMAC pair to the app's public webhook endpoint while forging the `shop-domain` header to a victim shop's domain, and/or forging the `topic`/`webhook-id` headers to a different value. `Utils::HmacValidator.validate` will still return `true`, because it never inspects the headers — it only recomputes the HMAC over `@raw_body` [5](#0-4) . `Registry.process` then invokes the registered handler for the forged `topic` with `shop:` set to the forged victim domain [6](#0-5) .

This is a design asymmetry introduced by this gem itself, not merely an artifact of Shopify's wire protocol: the sibling implementer of the same `Utils::VerifiableQuery` interface, `Auth::Oauth::AuthQuery`, deliberately folds `shop` into its `to_signable_string` so the shop identity is cryptographically bound to the signature during OAuth callback validation [7](#0-6) . `Webhooks::Request` does not apply the same binding for `shop`/`topic`/`webhook_id`, despite implementing the identical `VerifiableQuery` interface [1](#0-0) .

### Impact Explanation
Any app merchant (an "unprivileged" tenant relative to other tenants of the same multi-tenant app) can forge webhook deliveries that the app attributes to a different (victim) shop and/or a different topic than what was actually signed, purely by replaying their own genuine body+HMAC pair with spoofed headers. Depending on what the app's handlers do with `WebhookMetadata#shop`/`#topic` (e.g. `app/uninstalled` cleanup, `customers/redact`/`shop/redact` GDPR handlers, order/customer data ingestion keyed by `shop`), this enables cross-tenant data corruption, spoofed GDPR erasure requests against a victim shop, or false uninstall/lifecycle events attributed to a shop that never sent them — this is a cross-tenant access impact.

### Likelihood Explanation
Likelihood is bounded by the fact that the attacker must be able to obtain at least one legitimate body+HMAC pair from a real webhook delivery to the app (trivial for any merchant who installs the app themselves, since they receive real webhooks for their own shop) and must be able to reach the app's public webhook endpoint directly (bypassing Shopify's delivery infrastructure), which any internet host can do since the endpoint is a plain HTTP route.

### Recommendation
Bind `shop`, `topic`, and `webhook_id` into the HMAC-signed payload analogous to `Auth::Oauth::AuthQuery#to_signable_string`, or independently verify `request.shop` against a shop the app has an active session/installation record for, and verify `request.topic` is consistent with the body content, before dispatching to a handler in `Registry.process`.

### Proof of Concept
1. App merchant A installs the target app; Shopify delivers a legitimate webhook to the app's endpoint with body `B` and header `x-shopify-hmac-sha256: HMAC(secret, B)`.
2. Attacker (merchant A, or anyone who captured that body+HMAC pair) sends a forged HTTP POST directly to the app's webhook route with the same raw body `B` and HMAC header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and, if desired, a different `x-shopify-topic`.
3. `Utils::HmacValidator.validate` returns `true` because it only validates `B` against the HMAC [5](#0-4) .
4. `Registry.process` looks up the handler for the forged topic and invokes it with `shop: "victim-shop.myshopify.com"` [6](#0-5) , causing the app to perform shop-scoped side effects (data mutation, cleanup, redaction) attributed to a shop that never sent the webhook.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
