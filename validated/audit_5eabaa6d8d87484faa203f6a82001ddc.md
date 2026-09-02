### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , so `Utils::HmacValidator.validate` only proves the request body was signed by the app's client secret; it proves nothing about the `shop`, `topic`, `webhook_id`, or `api_version` values, which are all read straight from attacker-controllable HTTP headers [2](#0-1) . `Registry.process` validates only the HMAC and then dispatches the handler using the unauthenticated `request.shop` header [3](#0-2) .

### Finding Description
This mirrors the reported bug class: a downstream action (`cancelTransaction`/here, webhook dispatch keyed by shop) trusts an unverified field (`target timelock`/here, `shop-domain` header) instead of the value that was actually bound to the verified data. The equality that should hold is:

`shop bound by HMAC == shop used to key/dispatch the webhook`

but in this gem the actual binding is:

`shop bound by HMAC == nothing` (only `raw_body` is signed) vs. `shop used to key/dispatch == arbitrary attacker header`

Since a single app's `client_secret` is shared across every shop that installs that app, any merchant who legitimately installs the app on their own store receives genuinely-HMAC-valid `(raw_body, hmac)` pairs from Shopify. That attacker-controlled merchant can then replay the exact same `raw_body`/`hmac` to the app's webhook endpoint while substituting the `shopify-shop-domain` (and/or `shopify-topic`, `shopify-webhook-id`, `shopify-api-version`) header for a different, victim shop domain. `HmacValidator.validate` still returns `true` because it only recomputes the signature over `raw_body` [4](#0-3) , and `Registry.process` forwards the spoofed `shop` straight into `WebhookMetadata` without any additional binding check [5](#0-4) .

### Impact Explanation
An app handler that trusts `data.shop` to key its own per-tenant storage (a pattern the gem's own documentation explicitly recommends: `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) can be made to write/process legitimate-looking webhook payloads under the identity of a shop that never sent them, and without ever compromising or acting on behalf of that shop's real session. This crosses the tenant isolation boundary the HMAC check is supposed to enforce, matching the "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is low-to-medium: it requires the attacker to (a) be a genuine merchant who can install the target public app on their own store to obtain a validly-signed webhook, and (b) know/guess a victim shop's `myshopify.com` domain (these are often discoverable/public). No secrets, tokens, or privileged access are required — only observation of traffic the attacker legitimately receives and a header rewrite when replaying to the app's own public webhook endpoint.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the HMAC-signable content, or independently verify `request.shop` against the app's own record of installed/authorized shops before dispatching to the handler, rather than trusting the header value once the body HMAC passes.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`, registers for a webhook topic, and captures a legitimate webhook delivery: `raw_body = B`, header `shopify-hmac-sha256 = H` (valid because `HMAC(client_secret, B) == H`).
2. Attacker POSTs to the app's webhook endpoint with the same `raw_body = B` and `shopify-hmac-sha256 = H`, but sets `shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers, `Utils::HmacValidator.validate(request)` succeeds (it only checks `B`/`H`) [6](#0-5) .
4. `Registry.process` calls the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed B, ...)` [7](#0-6) , causing the app to process attacker-controlled webhook content under the victim shop's identity.

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
