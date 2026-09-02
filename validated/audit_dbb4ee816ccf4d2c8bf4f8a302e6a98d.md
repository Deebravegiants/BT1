## Title
Webhook `shop`, `topic`, and `webhook_id` are read from unauthenticated HTTP headers while the HMAC only covers the raw body — ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signable content solely from the raw request body, but the `shop`, `topic`, and `webhook_id` values that `ShopifyAPI::Webhooks::Registry.process` uses to authorize/dispatch the webhook and to construct the `WebhookMetadata` handed to the app's handler are taken directly from HTTP headers that are never part of the signed bytes. Any caller who possesses one valid `(body, hmac)` pair — trivially obtainable by any merchant/tenant who has installed the app and receives their own legitimate webhook deliveries — can replay that pair to the app's public webhook endpoint while freely setting the `shop-domain`, `topic`, and `webhook-id` headers to arbitrary values.

### Finding Description
`Utils::HmacValidator.validate` checks the request by calling `verifiable_query.to_signable_string` and comparing its HMAC against `verifiable_query.hmac`: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw body: [2](#0-1) 

But `shop`, `topic`, and `webhook_id` are derived from HTTP headers, entirely outside the HMAC-covered bytes: [3](#0-2) 

`Registry.process` validates only the body-HMAC, then trusts the header-derived `topic` to select a handler and the header-derived `shop`/`webhook_id` to build the metadata passed to that handler: [4](#0-3) 

The identity binding that is broken: `HMAC-verified(bytes) == identity(shop, topic, webhook_id)` acted on by the handler. In reality, `HMAC-verified(bytes) == body only`; `shop`/`topic`/`webhook_id` are unauthenticated attacker-controlled headers.

### Impact Explanation
Any tenant of a multi-tenant app (an "unprivileged" party relative to other merchants using the same app) that receives even one legitimate webhook delivery for their own store obtains a valid `(raw_body, hmac)` pair signed with the app's `client_secret`. They can replay this exact body+hmac to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain and/or the `x-shopify-topic`/`x-shopify-webhook-id` headers with different values. `Registry.process` will accept the HMAC (it only checks the body) and dispatch attacker-chosen data to a handler under an arbitrary shop identity and/or arbitrary topic of the attacker's choosing. This is a cross-tenant identity-spoofing primitive: the host application's webhook handler executes business logic (e.g. order creation/cancellation, app/uninstalled, GDPR, fulfillment events) believing it originates from a different tenant than the one that actually produced the signed bytes, without needing the victim's access token or any secret beyond what a normal merchant already receives.

### Likelihood Explanation
Any app merchant is, by construction, sent real webhooks whose bodies they can trivially trigger for topics under their control (e.g., creating their own order triggers `orders/create` with content they choose within the JSON structure). No credential beyond ordinary use of the app is required, and the attack is a single crafted HTTP POST to the app's public webhook URL with substituted headers. The vulnerability is directly reachable through this gem's own `Webhooks::Request`/`Registry.process` API, not through any host-app misuse.

### Recommendation
Bind `shop`, `topic`, and `webhook_id` into the HMAC-signable representation (or otherwise authenticate them, e.g. by requiring the caller to confirm the header-derived shop against a known/installed shop record with an active session before dispatch), so `Utils::HmacValidator.validate` fails whenever these header values do not match what the signature actually protects. At minimum, document and enforce that `Registry.process` must not use header-only-derived `shop`/`topic`/`webhook_id` as trusted dispatch/attribution keys without cross-checking them against the signed payload content or a known-shop registry.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and triggers a webhook they control the content of, e.g. `orders/create`, capturing the raw POST body `B` and the `x-shopify-hmac-sha256` header `H` that Shopify sends (a valid HMAC over `B` computed with the app's `client_secret`).
2. Attacker sends a new POST directly to the app's public webhook endpoint with:
   - Body: the exact captured `B`
   - Headers: `x-shopify-hmac-sha256: H` (unchanged), `x-shopify-shop-domain: victim-shop.myshopify.com` (spoofed), `x-shopify-topic: orders/create` (or any other registered topic), `x-shopify-webhook-id: <arbitrary>`.
3. The app calls `ShopifyAPI::Webhooks::Registry.process(ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: spoofed_headers))`.
4. `Utils::HmacValidator.validate` succeeds because it only verifies `B` against `H` [5](#0-4) 
   and the handler is invoked with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)` [6](#0-5) , causing attacker-chosen data to be processed under a spoofed tenant identity.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
