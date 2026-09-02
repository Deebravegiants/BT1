Confirmed: `to_signable_string` for `Webhooks::Request` returns only `@raw_body` [1](#0-0) , and `HmacValidator.validate` computes the signature purely from that signable string [2](#0-1) , while `shop` is read directly from the unauthenticated `shopify-shop-domain` header [3](#0-2) . `Registry.process` trusts `request.shop` for dispatch after only validating the HMAC over the body [4](#0-3) .

### Title
Webhook shop attribution is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#hmac` and `#to_signable_string` bind the HMAC signature only to the raw request body, never to the `shop-domain`/`x-shopify-shop-domain` header that `Registry.process` uses to attribute the webhook to a specific shop. Because Shopify signs webhooks with the app's single `client_secret` (the same secret across all shops that install the app), any signature that is valid for a given body is valid for that body regardless of which shop header accompanies it.

### Finding Description
`Webhooks::Request` implements `Utils::VerifiableQuery`. Its `to_signable_string` returns `@raw_body` only: [1](#0-0) 

`shop` is a separate accessor pulled straight from request headers, entirely outside anything the HMAC covers: [3](#0-2) 

`Utils::HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it against the received HMAC — it never incorporates the shop header into the signed material: [2](#0-1) 

`Webhooks::Registry.process` validates the HMAC and then dispatches to the app's handler using `request.shop` as the tenant identifier, with no separate check that ties the shop header to the signed body: [4](#0-3) 

Since a single app-level `api_secret_key` is used to sign webhooks for every shop that installs the app (there is no per-shop signing key in this gem's model — see `HmacValidator.validate` using `Context.api_secret_key`) [5](#0-4) , a valid `(body, hmac)` pair captured from a webhook delivered for shop A remains a *valid* `(body, hmac)` pair when replayed with the `shop-domain` header changed to shop B. `Registry.process` will accept it — `Utils::HmacValidator.validate` only checks the body/HMAC pair, and passes `request.shop` (attacker-controlled, unauthenticated) straight into `WebhookMetadata` for the handler to act on. This breaks the intended binding `hmac == HMAC(body ‖ shop)`, effectively only enforcing `hmac == HMAC(body)`.

### Impact Explanation
This lets an unprivileged internet user who controls one shop that has installed the app (or who simply captures/replays a single legitimately-signed webhook payload) cause the app to process a webhook body while attributing it to an arbitrary victim shop domain of their choosing. Any app logic keyed off `WebhookMetadata#shop` (e.g., writing merchant/customer data indexed by shop, triggering shop-scoped side effects, honoring `shop/redact` or `customers/data_request` mandatory compliance webhooks) can be poisoned or forged for a shop the attacker does not operate — a cross-tenant integrity violation reachable purely through this gem's HMAC verification, matching the "cross-tenant access" impact class.

### Likelihood Explanation
Medium-High: no access token or `client_secret` leak is required. An attacker only needs the ability to deliver/replay an HTTP request to the app's webhook endpoint with a valid `(body, hmac)` pair — achievable by an app's own shop attacker sending itself a real webhook (e.g. by performing an action that triggers `orders/create` in their own store) and then replaying the exact body/HMAC with a forged `shop-domain` header.

### Recommendation
Include the shop domain (and ideally topic/api-version) in the signed/verified material, or independently verify that the `shop-domain` header matches a shop-specific expectation before trusting `request.shop` in `Registry.process`. At minimum, document that consuming apps must not treat `WebhookMetadata#shop` as authenticated unless they perform their own additional binding (e.g., checking it against the session/shop they registered the webhook for).

### Proof of Concept
1. App installs on `attacker-shop.myshopify.com` and registers a webhook handler for `orders/create`.
2. Attacker triggers `orders/create` in their own store, causing Shopify to POST a webhook with header `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, some `raw_body`, and `X-Shopify-Hmac-Sha256: HMAC(raw_body, client_secret)`.
3. Attacker captures this request, then re-sends it to the app's webhook endpoint with the header changed to `X-Shopify-Shop-Domain: victim-shop.myshopify.com`, keeping `raw_body` and the HMAC value identical.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(raw_body, client_secret)` and finds it matches — validation passes because the header is never part of the signed string (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb:26-31`).
5. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, so the app processes attacker-controlled data as if it originated from the victim shop.

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
