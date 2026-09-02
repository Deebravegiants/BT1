### Title
Webhook HMAC Does Not Cover Shop, Topic, or Webhook-Id Headers, Enabling Cross-Tenant Webhook Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC-signable string from the raw request body only, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers and passed straight into the handler as trusted identity fields.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely with `Utils::HmacValidator.validate(request)`, which calls `request.to_signable_string`: [1](#0-0) 

`to_signable_string` returns only `@raw_body`: [2](#0-1) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all pulled from headers that are never mixed into the signed content: [3](#0-2) 

`HmacValidator.validate_signature` compares `verifiable_query.hmac` against `HMAC(secret, to_signable_string)` — i.e., only over the body: [4](#0-3) 

After validation succeeds, `Registry.process` uses the unauthenticated `request.topic` to select the handler and forwards the unauthenticated `request.shop` (and `webhook_id`/`api_version`) straight into `WebhookMetadata`, which the app's handler treats as the authoritative tenant/topic identity: [5](#0-4) 

This is exactly the pattern called out in the rules: a field (`shop`, `topic`, `webhook_id`) that is acted on by the application but not covered by the HMAC. Since the `client_secret` used to sign webhooks is per-app (shared across every merchant/shop that installs the app), an attacker who has installed the app on their own shop can trigger a real webhook, capture a valid `(raw_body, hmac)` pair signed with the app's secret, and then replay that exact body+HMAC to the app's webhook endpoint while forging the `x-shopify-shop-domain` and `x-shopify-topic` headers to claim any other tenant/topic. `HmacValidator.validate` will report the request as authentic because it only checks the body, and `Registry.process` will hand the forged `shop`/`topic` to the host application's handler as if Shopify itself vouched for them.

### Impact Explanation
This breaks the identity binding `shop-authenticated-by-HMAC == shop-acted-upon-by-handler`. An attacker who is merely an installer of the app on their own store (an unprivileged actor with respect to other merchants) can make the app process attacker-chosen webhook bodies under a spoofed `shop` value and spoofed `topic`, causing the host application to attribute/act on events for a different tenant. This is a cross-tenant confusion / spoofing primitive directly reachable through this gem's own webhook-processing code, matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Likelihood is realistic for any app that installs on multiple shops: any merchant who can install the app (a normal, unprivileged flow) can obtain a validly-signed `(body, hmac)` pair from their own legitimate webhook deliveries, since the signing secret is the app's `client_secret`, not shop-specific. Forging headers on an HTTP request to the app's own public webhook endpoint requires no special access.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the signed/verified material — or, since Shopify's webhook HMAC scheme is defined to cover only the raw body, the gem should treat the header-derived `shop`/`topic` as merely advisory and document/require that host applications re-validate them against known-registered webhook subscriptions (e.g., matching `webhook_id` to a subscription actually created for that specific shop) before trusting `WebhookMetadata#shop`/`#topic`. At minimum, `Registry.process` should cross-check that the `webhook_id` in the request actually belongs to the `shop` in the request via a server-side lookup before dispatching to the handler, rather than trusting the headers outright once the body-only HMAC passes.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`, obtaining an app installation that shares the same `client_secret` as all other installs.
2. Trigger any webhook event (e.g., `orders/create`) on `attacker.myshopify.com`; capture the raw POST body and the `X-Shopify-Hmac-Sha256` header — this HMAC is valid because `HmacValidator` only signs `@raw_body`.
3. Replay this exact `(raw_body, hmac)` pair to the app's webhook endpoint, but override the headers:
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
   - `X-Shopify-Topic: orders/create` (or any registered topic)
4. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:13-22`) returns `true` because only the body is checked.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-199`) dispatches to the handler with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: <attacker's body>, ...)`, causing the host app to process attacker-chosen data as if it originated from `victim-shop.myshopify.com`.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
