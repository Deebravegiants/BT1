### Title
Webhook shop-domain identity spoofing via HMAC that only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by checking the HMAC over the raw request body, then hands the caller a `WebhookMetadata` struct whose `shop` field is taken from the `x-shopify-shop-domain`/`shopify-shop-domain` header — a value that is never included in the HMAC computation. This breaks the intended binding `hmac == sign(body ‖ shop)`; in this implementation the equality actually enforced is only `hmac == sign(body)`, letting an attacker with a valid HMAC for some body swap in an arbitrary `shop` value that the host application's handler will trust as the webhook's tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and `shop` is read straight from an unauthenticated header with no relation to the signed bytes: [2](#0-1) 

`Utils::HmacValidator.validate` verifies exactly this signable string against `Context.api_secret_key` (a single, app-wide secret shared across every shop that has the app installed): [3](#0-2) 

`Registry.process` uses only this body-only HMAC check as its authentication gate, then forwards the unauthenticated `shop` header straight into `WebhookMetadata` that is passed to the app's handler: [4](#0-3) [5](#0-4) 

Compare this to the OAuth callback flow, where `shop` *is* part of the signed content (`AuthQuery#to_signable_string` includes `shop`): [6](#0-5) 

So the gem's own OAuth path treats `shop` as a value that must be bound to the HMAC, while the webhook path does not — an inconsistent identity binding within the same library.

Exploit path: an attacker who has the target app installed on their own shop (an ordinary, unprivileged merchant relationship — no elevated credentials needed) can trigger any webhook topic with a body of their choosing (e.g. by creating/renaming a resource that produces predictable JSON), capture the resulting HTTP request that Shopify sends to the app's webhook endpoint (containing a valid `hmac-sha256` computed by Shopify with the app's real secret, and a `shop-domain` header equal to the attacker's own shop), and then replay that exact body+HMAC to the same endpoint while substituting the `shop-domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds because it only checks the body, and `Registry.process` calls the registered handler with `WebhookMetadata.shop` equal to the spoofed victim shop.

### Impact Explanation
This crosses a tenant boundary: `shop` is the value host applications use as the tenant/session key to decide whose data to create, update, or delete in response to a webhook (e.g., matching `data.shop` to a stored session to look up the merchant's records). Because the gem supplies an unauthenticated `shop` value alongside an authenticated body, a malicious merchant can make the app believe events belong to a different, victim shop, causing cross-tenant data corruption or unauthorized actions attributed to a shop the attacker does not control. This matches the "Critical - cross-tenant access" impact category, since the trust boundary broken is exactly the shop/tenant identity that the HMAC is supposed to authenticate.

### Likelihood Explanation
Requires only an ordinary, unprivileged relationship with the target app (installing it on any shop, including a free/trial shop, and being able to trigger a webhook with attacker-influenced body content) plus the ability to replay/modify an HTTP request header — no access to `api_secret_key`, access tokens, or the app's infrastructure is needed. This is a realistic, low-barrier likelihood for any app built directly on the documented `Registry.process`/`WebhookHandler` API from `docs/usage/webhooks.md`.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the value verified by the HMAC, or at minimum require host applications to cross-check `WebhookMetadata.shop` against an existing, previously-established session/tenant record before trusting it, and document this requirement prominently since `Registry.process` currently implies the shop value is authenticated once HMAC validation passes.

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com` and adds an `orders/create` webhook handler in the host app via `ShopifyAPI::Webhooks::Registry.add_registration`.
2. Attacker creates an order producing JSON body `B`; Shopify POSTs to the app's webhook route with headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: H` (H = HMAC-SHA256(secret, B)), and body `B`.
3. Attacker captures this request and resends it to the same route, replacing only the header: `x-shopify-shop-domain: victim.myshopify.com`, keeping body `B` and header `H` unchanged.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate`, which recomputes HMAC over `B` only and matches `H` — validation passes.
5. The registered `WebhookHandler#handle` is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", body: B, ...)`, causing the host app to process attacker-controlled data as though it originated from the victim shop.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
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
