## Title
Webhook `shop` (and topic/api-version/webhook-id) headers are trusted for tenant identification but are not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw body only, while the tenant-identifying `shop` value is read from an unauthenticated HTTP header. `Registry.process` forwards this unauthenticated `shop` value straight to the host application's webhook handler as the trusted tenant identifier, breaking the intended binding `shop == HMAC-covered-tenant`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` (and `topic`, `api_version`, `webhook_id`) are pulled straight from HTTP headers with no cryptographic binding to the body or to each other: [2](#0-1) 

`Utils::HmacValidator.validate` verifies `verifiable_query.hmac` against `verifiable_query.to_signable_string`, i.e. only the raw body bytes are authenticated: [3](#0-2) 

`Registry.process` checks only this body HMAC, then immediately trusts `request.shop` (the unauthenticated header) as the tenant identifier passed to the app's handler: [4](#0-3) 

The identity binding the gem implicitly promises to the host application is: *`shop` returned by `Registry.process`'s `WebhookMetadata` == the tenant whose signed payload was verified*. In reality the equality that holds is only `hmac == HMAC(raw_body, api_secret_key)`; `shop` is disjoint from what is verified. Because the `api_secret_key` (the app's `client_secret`) is the same for every shop that installs the app, any user who installs the app on their own store receives a genuinely-signed webhook (valid body + hmac pair) for that store. That same `(raw_body, hmac)` pair remains valid when replayed to the app's webhook endpoint with the `x-shopify-shop-domain` header changed to a victim shop, since the signature check never inspects the header.

### Impact Explanation
An unprivileged user who can install the target app on their own (attacker-controlled) shop can capture a legitimately-signed webhook and replay it with a forged `shop` header pointing at a different, victim tenant. Because `Registry.process` passes this attacker-controlled `shop` value to the host application's handler as the authoritative tenant identifier, this allows cross-tenant data injection/action: the host application will process the attacker's payload as if it belongs to the victim shop (e.g., updating victim-associated records, triggering victim-specific business logic, or resolving the wrong per-shop session for follow-up API calls keyed by `shop`). This satisfies the "cross-tenant access" high/critical impact bar since it breaks the shop-to-payload identity binding using only capabilities available to any user of the app (installing it on their own store).

### Likelihood Explanation
Likelihood is high for apps that key any state, session lookup, or authorization decision off of `WebhookMetadata#shop` from `ShopifyAPI::Webhooks::Registry.process` without independently cross-checking the shop against the payload contents. Any user able to install the app (a completely unprivileged action for any public/embedded app) can obtain a valid `(raw_body, hmac)` pair from their own store's webhooks and replay it with a modified `shop` header, since nothing in the gem ties the header to the signature.

### Recommendation
Include the `shop` (and ideally `topic`/`api-version`/`webhook-id`) values in the signable content that is HMAC-verified, or otherwise cryptographically bind them to the verified payload (e.g., require the body to embed/replicate the shop and compare it against the header before trusting it). At minimum, document prominently that `request.shop` is not authenticated by `HmacValidator.validate` and must not be used by host applications as a trusted tenant identifier without additional verification (e.g., cross-checking against a shop value embedded in the JSON body or against known/expected shop lists).

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` (normal, unprivileged action).
2. Attacker triggers a subscribed webhook topic (e.g. `orders/create`) on their own store. Shopify sends the app's webhook endpoint a request signed with the app's shared `client_secret`:
   - `x-shopify-hmac-sha256: <valid HMAC of raw_body>`
   - `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - `x-shopify-topic: orders/create`
3. Attacker captures the exact `raw_body` and `x-shopify-hmac-sha256` value from step 2.
4. Attacker sends a new HTTP request directly to the app's public webhook endpoint using the identical `raw_body`/`hmac` header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `raw_body` only — it matches, so validation passes: [5](#0-4) 
6. The handler is invoked with `shop: "victim-shop.myshopify.com"` even though the payload was generated for/by the attacker's shop: [6](#0-5) 
7. Any host application logic keyed on this `shop` value (session lookup, per-shop data writes, business logic) now operates cross-tenant using attacker-supplied data.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-33)
```ruby
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
