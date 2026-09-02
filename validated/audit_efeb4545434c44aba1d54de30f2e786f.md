## Title
Webhook HMAC signs only the raw body, letting an unauthenticated `shop-domain` header spoof tenant identity in `ShopifyAPI::Webhooks::Registry.process` — ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so the HMAC signature that `Registry.process` verifies covers *only the JSON body*, not the `shop-domain`, `topic`, or `webhook-id` headers that the same method uses to build the `WebhookMetadata` dispatched to the app's handler. This breaks the identity binding `shop verified by HMAC == shop acted on by the handler`.

### Finding Description
`Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` and compares it against the `hmac` value: [1](#0-0) [1](#0-0) 

For `ShopifyAPI::Webhooks::Request`, `to_signable_string` returns only `@raw_body`: [2](#0-1) 

Yet `shop`, `topic`, and `webhook_id` are all read straight from unauthenticated HTTP headers: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately uses `request.shop` (and `request.topic`, `request.webhook_id`) — none of which are covered by that HMAC — to build the metadata handed to the app's handler: [4](#0-3) 

So the equality the code implicitly assumes is:
`shop authenticated by HMAC == shop used to dispatch WebhookMetadata`

but in reality:
`shop covered by HMAC (none, since only raw_body is signed) ≠ shop read from the spoofable "shop-domain" header`

Because the HMAC secret (`api_secret_key`) is a single shared secret for the whole app across *all* shops that install it (not shop-specific), any (body, hmac) pair that Shopify legitimately delivers for **any** shop where the app is installed is a valid signature for that exact body regardless of which shop header accompanies it. An attacker who is a normal, unprivileged Shopify merchant can install the app on their own store, trigger any webhook event on their own store, capture the resulting `(raw_body, X-Shopify-Hmac-Sha256)` pair, and replay it directly to the app's public webhook endpoint with an arbitrary `X-Shopify-Shop-Domain` header (e.g., a victim shop). `Registry.process` will accept it, since only the untouched body's HMAC is checked, and will hand the handler `WebhookMetadata` claiming the data belongs to the victim shop.

### Impact Explanation
This crosses the tenant boundary the gem is meant to enforce: the `shop` value passed to the webhook handler — normally used by host apps to select which tenant's records to update — is not bound to the HMAC that was just validated. An attacker with no privileges over the victim tenant (and no access to `api_secret_key`, access tokens, or any victim credentials) can inject attacker-controlled body content tagged with the victim shop's identity into the app's webhook processing pipeline. Depending on the handler, this enables cross-tenant data injection/corruption using only a self-service app installation and a replayed HTTP request — matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high for any app that: (1) is public/installable by arbitrary merchants (a normal precondition for using this gem's webhook API), and (2) uses the `shop` field from `WebhookMetadata` to select tenant state, which is the documented/expected usage pattern (`ShopifyAPI::Webhooks::WebhookHandler#handle` receives `shop` precisely for this purpose). No secret material, MITM, or social engineering is required — only a self-installed trial/dev store and a basic HTTP client capable of setting custom headers.

### Recommendation
Bind the `shop-domain` (and ideally `topic`/`webhook-id`) header values into the signed payload verification, or otherwise cryptographically bind them to the raw body before trusting `request.shop` for tenant dispatch — e.g., include the shop domain in `to_signable_string`, or require host apps to independently verify `request.shop` against a maintained list of shops that have installed the app before trusting body content tied to that shop, and make this an enforced, documented step in `Registry.process` rather than an implicit external responsibility.

### Proof of Concept
1. Attacker creates a Shopify development/trial store `attacker-shop.myshopify.com` and installs the target app (public/self-serve installation, no privileged credentials needed).
2. Attacker performs an action on `attacker-shop` that triggers a subscribed webhook (e.g., updates a product), causing Shopify to POST to the app's webhook endpoint with:
   - Body: `{"id": ..., "title": "malicious payload", ...}`
   - Headers: `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>`, `X-Shopify-Topic: products/update`
3. Attacker captures this exact `(raw_body, hmac)` pair (e.g., via their own logging/inspection tooling for a request they legitimately received, or by hosting the endpoint through a tool they control).
4. Attacker sends a new HTTP POST directly to the app's public webhook URL with the identical body and `X-Shopify-Hmac-Sha256` header, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new` parses this, and `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only recomputes the HMAC over `raw_body` (line `lib/shopify_api/webhooks/request.rb:36-38`), which is unchanged.
6. `Registry.process` dispatches `WebhookMetadata.new(topic: "products/update", shop: "victim-shop.myshopify.com", body: <attacker JSON>, ...)` to the app's handler, which now processes attacker-controlled data as if it belonged to `victim-shop`.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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
