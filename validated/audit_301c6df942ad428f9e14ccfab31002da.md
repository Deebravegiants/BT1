### Title
Webhook shop/topic identity is not bound by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop`, `topic`, `webhook_id`, and `api_version` fields that `Registry.process` uses to route and attribute the event are read directly from unauthenticated HTTP headers. Anyone who can obtain one genuine `(raw_body, hmac)` pair signed with the app's shared `api_secret_key` (e.g., by installing the app on their own store and triggering any webhook) can replay that exact body/HMAC pair while freely rewriting the `x-shopify-shop-domain` and `x-shopify-topic` headers, causing the app to process the event as if it originated from a different topic and a different, victim shop.

### Finding Description
`Utils::HmacValidator.validate` only proves that the caller knows the shared `api_secret_key` used to sign `verifiable_query.to_signable_string`. For webhooks, `to_signable_string` returns solely the raw body: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors are read straight from headers, which are not part of the signed content at all: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately trusts these header-derived fields to build the `WebhookMetadata` dispatched to the app's handler: [3](#0-2) 

`HmacValidator.validate_signature` compares the HMAC purely against the body bytes and the shared secret: [4](#0-3) 

The identity binding that should hold is: `shop header == shop that produced this exact signed body`. Because the signature covers only the body, this equality is never checked — an attacker who has a valid `(body, hmac)` pair from any shop where the app is installed (including their own store) can present the same pair with a different `shop`/`topic` header value, and `Registry.process` will accept it as authentic for the attacker-chosen shop/topic.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook events. A merchant/attacker who legitimately installs the app on their own shop can:
1. Trigger any webhook topic on their own store to obtain a valid `(raw_body, hmac)` pair signed with the app's `api_secret_key`.
2. POST directly to the app's webhook endpoint (there is no IP allow-listing or replay/nonce protection in this code path) with the same body and `hmac-sha256` header, but with `x-shopify-shop-domain` and `x-shopify-topic` set to any other installed shop and any topic.
3. `Registry.process` will pass HMAC validation and hand the handler a `WebhookMetadata` claiming the event is for the victim shop/topic, even though the content and origin are entirely attacker-controlled.

Depending on what the host app's webhook handlers do with `shop` (e.g., look up/mutate the victim's stored session, trigger billing/shop-scoped business logic, or process `app/uninstalled`, `shop/redact`, `app_subscriptions/update` type flows), this enables cross-tenant data manipulation using only the ability to install the app on any store — something any internet user with a Shopify dev/trial store can do.

### Likelihood Explanation
Likelihood is high: no privileged credential is needed beyond installing the target app on a shop the attacker controls (a normal, unprivileged action), and the webhook endpoint is a public HTTP route with no additional binding of headers to the signed payload.

### Recommendation
Include the routing/identity fields (`shop`, `topic`, `webhook_id`, `api_version`) in the signable content, or otherwise cryptographically bind them to the payload before trusting them for dispatch — e.g., require them to be present in and matched against the parsed body, or use Shopify's `X-Shopify-Webhook-Id` combined with a nonce/timestamp check plus verifying the `shop` domain against session storage before invoking handler logic that has tenant-scoped side effects.

### Proof of Concept
1. Install the app on `attacker-shop.myshopify.com`; trigger a real webhook (e.g., `orders/create`) and capture the raw POST body and its `x-shopify-hmac-sha256` header — this is a valid `(body, hmac)` pair signed with the app's `api_secret_key`.
2. Send a new POST directly to the app's webhook endpoint with the identical body and `hmac-sha256` header, but set:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
   - `x-shopify-topic: app/uninstalled` (or any topic of choice)
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks the (unchanged) body against the (unchanged) HMAC — validation succeeds.
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and the attacker-chosen `topic`, despite the event never having originated from Shopify for that shop/topic.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
