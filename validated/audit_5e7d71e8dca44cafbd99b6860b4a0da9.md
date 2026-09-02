### Title
Webhook HMAC verifies only the request body, so the `shop` domain used to route/tenant-scope a webhook is unauthenticated — cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop` (and `topic`, `api_version`, `webhook_id`) straight from HTTP headers, but the HMAC signature that `HmacValidator` checks only covers the raw request body. Any caller who can obtain one validly-signed webhook body (e.g., by installing the target app on their own store) can replay that body while substituting the `x-shopify-shop-domain` header for a victim shop, and the signature will still validate — because the shop was never part of what was signed.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read from the `shopify-shop-domain`/`x-shopify-shop-domain` header, entirely independent of the body or the HMAC: [2](#0-1) [3](#0-2) 

`Utils::HmacValidator.validate` computes/compares the HMAC only against `verifiable_query.to_signable_string` (i.e., the body for webhooks), using the app-wide shared `Context.api_secret_key`: [4](#0-3) 

`Webhooks::Registry.process` validates the HMAC, then immediately trusts `request.shop` (the unauthenticated header) as the tenant identity passed to the app's handler: [5](#0-4) 

The equality that should hold is: `shop covered by the verified HMAC == shop used as the tenant/session key handed to the handler`. In this code, the left side is empty (shop is never signed) while the right side is `request.shop`, an attacker-controllable header. The two are never the same value, so the binding is broken.

### Impact Explanation
Any unprivileged internet user can install the target app on a store they control (a standard, unprivileged action — installing a public Shopify app requires no special access) and thereby obtain a body + HMAC pair that is valid under the app's shared `api_secret_key`. Because that same shared secret and signing scheme is used for every shop the app is installed on, and the `shop` header is excluded from the signed content, the attacker can resend the exact same signed body with the `shop` header rewritten to a victim shop's domain. `Webhooks::Registry.process` will accept the HMAC (it only checks the body) and dispatch the handler with `shop: <victim-shop>`, `body: <attacker-supplied-json>`. Any consuming application that uses `WebhookMetadata#shop` to select per-tenant storage, credentials, or business logic (the documented and expected usage pattern shown in `docs/usage/webhooks.md`) will process attacker-controlled data under a victim tenant's identity — a cross-tenant data/action injection.

### Likelihood Explanation
Likelihood is moderate-to-high in any deployment that relies solely on this gem's `Registry.process`/`HmacValidator` for webhook authenticity (as documented) without independently cross-checking the shop domain against an out-of-band trusted webhook delivery channel. No credentials, tokens, or `api_secret_key` need to be known — only the ability to install the app on an attacker-owned shop, which is normal, unprivileged usage of a public app.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the signed payload verification, or independently verify that the shop delivering the webhook matches a shop that legitimately has this app installed (e.g., cross-reference against stored, previously-authenticated sessions) before trusting `request.shop`/`WebhookMetadata#shop` for tenant-scoped operations. At minimum, document prominently that `shop` in `Webhooks::Request`/`WebhookMetadata` is unauthenticated and must not be used as a sole tenant-binding key.

### Proof of Concept
1. Attacker creates a development/trial store and installs the target Shopify app, causing Shopify to legitimately deliver a webhook (e.g., `orders/create`) with a valid `x-shopify-hmac-sha256` computed over the JSON body using the app's shared `api_secret_key`.
2. Attacker captures `raw_body` and its `hmac` header from this legitimate delivery.
3. Attacker (or a malicious script hitting the app's webhook endpoint directly, since Shopify's webhook endpoints are just public HTTP endpoints) resends the same `raw_body`/`hmac`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` returns `true` because it only re-hashes `raw_body`.
5. `Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) calls the registered handler with `shop: "victim-shop.myshopify.com"` and the attacker's JSON body, even though `victim-shop.myshopify.com` never sent this webhook.

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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
