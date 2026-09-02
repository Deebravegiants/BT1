### Title
Webhook shop-domain identity is not covered by the HMAC signature, allowing cross-tenant webhook impersonation - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `ShopifyAPI::Webhooks::Request#shop` is read from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC over the body only, then passes the unverified `request.shop` value into the handler as the tenant identity for the webhook event, breaking the binding: `shop authenticated by HMAC == shop acted upon`.

### Finding Description
`Utils::HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string`, and for `Webhooks::Request` that method returns `@raw_body` only: [1](#0-0) [2](#0-1) 

The `shop` accessor used downstream is derived purely from the `shop-domain` header, never included in the signed payload: [3](#0-2) 

`Registry.process` validates the HMAC against the body, but then trusts `request.shop` (the unauthenticated header) as the tenant identity handed to the app's webhook handler: [4](#0-3) 

Since a single Shopify app uses one `client_secret` shared across all shops that install it, the HMAC over the body is valid for *any* shop's webhook traffic under that app — it does not bind the signature to a specific shop. Because `shop-domain` is excluded from the signed string, the equality that should hold — `shop bound by HMAC == shop delivered to handler as data.shop` — does not hold: the header can be swapped by anyone controlling the HTTP request without invalidating the HMAC check.

### Impact Explanation
Any actor who can submit an HTTP request to the app's webhook endpoint (this is a public endpoint by design) and who possesses one valid `(raw_body, hmac)` pair for the app (e.g., because they have their own Shopify store installed on the same app and can capture their own legitimate webhook deliveries) can resend that exact same body+hmac pair while substituting the `shop-domain` header with a victim shop's domain. `Registry.process` reports the HMAC as valid (it only checks the body) and invokes the app's handler with `WebhookMetadata` claiming the payload belongs to the victim shop. This is a cross-tenant data confusion/injection: the app's business logic (queued jobs, database writes, order/customer state changes keyed by `shop`) can be manipulated to act as if attacker-controlled data originated from a different, unrelated merchant. This satisfies the "cross-tenant access" impact bar, because the tenant boundary (shop identity) that the gem is responsible for authenticating is bypassed for the purpose of routing/handling.

### Likelihood Explanation
Likelihood is high for any app that has multiple installs (the normal case for a public/multi-tenant Shopify app): an attacker just needs their own shop to install the app once to capture a valid signed webhook body, then can freely replay it with a forged `shop-domain` header against the same public webhook endpoint. No access token, `client_secret`, or privileged credential is required — only participation as a normal merchant using the app, which is an unprivileged-internet-user capability.

### Recommendation
Include the shop-identifying header (`shop-domain`) in the HMAC signable content, or otherwise cryptographically bind the shop domain to the signed payload, e.g., extend `Webhooks::Request#to_signable_string` to incorporate the `shop-domain` header (and ideally `topic`/`webhook-id`) so that any header tampering invalidates the signature, rather than trusting `request.shop` purely from unauthenticated header data.

### Proof of Concept
1. App installs are shared secret across shops; attacker installs the target app on `attacker-shop.myshopify.com` and lets Shopify deliver one legitimate webhook, capturing `raw_body` and its `X-Shopify-Hmac-Sha256` value (a normal merchant action, no special privilege).
2. Attacker POSTs to the same public webhook endpoint with the identical `raw_body`/`hmac-sha256` header, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds the request object; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `to_signable_string` (`raw_body` only) and succeeds because the body/hmac pair is unchanged. [5](#0-4) 
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the payload actually originated from the attacker's own shop, letting the attacker inject arbitrary attacker-controlled webhook content attributed to the victim tenant.

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
