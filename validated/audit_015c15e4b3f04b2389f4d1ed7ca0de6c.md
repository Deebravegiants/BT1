### Title
Webhook shop-domain is not covered by the HMAC signature, allowing cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body of the webhook request, and `shop` (from the `x-shopify-shop-domain` header) is read separately and never included in the HMAC-covered data. `Utils::HmacValidator.validate` therefore only proves that *some* party who knows the app's shared `api_secret_key` produced this exact body — it proves nothing about which shop the request is actually for. `Webhooks::Registry.process` trusts `request.shop` as the tenant identity once the HMAC check passes.

### Finding Description
The binding that should hold is: `hmac_verified(body, shop) == shop_used_for_processing`. Instead the code verifies `hmac_verified(body)` only, and separately reads `shop` from an unauthenticated header: [1](#0-0) 

`Utils::HmacValidator.validate` computes/compares the signature purely against `to_signable_string` (the raw body): [2](#0-1) 

`Registry.process` gates on that HMAC check, then constructs `WebhookMetadata` using `request.shop`, which is completely decoupled from the value that was actually signed: [3](#0-2) 

Because `api_secret_key` is a single, app-wide secret shared across every shop that installs the app (it is not shop-specific — see how it's reused verbatim for every merchant's OAuth/token-exchange flow in `lib/shopify_api/auth/oauth.rb` and `lib/shopify_api/auth/token_exchange.rb`), any merchant who installs the app can legitimately receive HMAC-valid `(body, hmac)` pairs from Shopify for their own shop. Since the `shop-domain` header is outside the signed payload, that same `(body, hmac)` pair remains valid if replayed to the app's public webhook endpoint with the `x-shopify-shop-domain` header rewritten to point at a different (victim) shop. `HmacValidator.validate` will still return `true` (the body/hmac pair is unchanged and correct), and `Registry.process` will hand the handler a `WebhookMetadata` claiming to be from the victim shop.

This is exactly the bug class in the reference report: a field that is acted upon (`shop`, used to route/attribute the webhook to a tenant) is not covered by the integrity check (the HMAC), so the two can be desynchronized by an attacker who controls one of them (the header) while reusing a value they legitimately obtained for the other (a valid body+hmac).

### Impact Explanation
This crosses a tenant boundary: a user who is only entitled to interact with the app as their own shop can make the host application process webhook data attributed to an arbitrary other shop (cross-tenant impersonation), potentially triggering handler logic (order sync, fulfillment automation, data writes, notifications, etc.) keyed to a victim shop's identity. This matches the "Critical – cross-tenant access" impact category.

### Likelihood Explanation
Requires only: (1) installing the app on the attacker's own shop — an ordinary unprivileged action available to any Shopify merchant, and (2) sending a normal HTTP POST to the app's public webhook receiver endpoint with a modified `x-shopify-shop-domain` header. No access token, no `api_secret_key` leak, and no privileged account is required, since the shared secret is never shop-specific and the header carrying tenant identity is outside the signed content. This is straightforward for anyone who can install the app once.

### Recommendation
Bind the shop identity into the verified data, e.g. include the `x-shopify-shop-domain` (and ideally topic/webhook-id) values in `to_signable_string`'s comparison, or — since Shopify's HMAC contract only covers the raw body — require the caller/host app to additionally validate that `request.shop` corresponds to a shop that is actually installed/known to the app (cross-check against stored sessions) before trusting it as a tenant identifier, and document this requirement prominently since the gem's current API silently implies HMAC validation is sufficient for full request authenticity including tenant identity.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a normal, unprivileged install).
2. Shopify sends a legitimate webhook to the app's endpoint, HMAC-signed with the app's shared `api_secret_key` over the JSON body, with header `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker captures this `(raw_body, x-shopify-hmac-sha256)` pair (e.g., by controlling infra that receives their own shop's webhooks, or via any legitimate access to their own webhook deliveries).
4. Attacker crafts a new HTTP POST directly to the app's public webhook endpoint using the **same** `raw_body` and `x-shopify-hmac-sha256` value, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new` parses this successfully; `Utils::HmacValidator.validate(request)` returns `true` because the signature check only depends on `raw_body` [4](#0-3) 
6. `Registry.process` invokes the topic handler with `WebhookMetadata.new(... shop: request.shop ...)` where `request.shop == "victim-shop.myshopify.com"`, even though nothing about the victim shop was ever verified [5](#0-4)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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
