### Title
Webhook `shop-domain` and `topic` headers are trusted for routing/tenant identity without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` signs only the raw request body, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers and passed straight into the app's handler as trusted identity data. `Webhooks::Registry.process` validates the HMAC and then unconditionally trusts `request.shop`/`request.topic` for dispatch, so any header value not covered by the signature can be forged as long as the attacker can supply *some* raw body + valid HMAC pair for the app's shared `api_secret_key`.

### Finding Description
`to_signable_string` for a webhook request is defined as just the body bytes: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are pulled from headers that are entirely outside of what gets signed: [2](#0-1) 

`Registry.process` validates the HMAC over the body only, then immediately trusts the unauthenticated `request.topic` and `request.shop` to route the payload and construct the metadata object handed to the app's handler: [3](#0-2) 

`WebhookMetadata#shop` is a plain `String` field with no binding back to the signature: [4](#0-3) 

The identity binding that should hold is: `bytes verified == bytes that determine which tenant (shop) the payload is attributed to`. Here that equality is broken — the HMAC only proves body integrity, not which shop or topic the body applies to. Because every shop installed on a given app shares the same `api_secret_key`, a body+HMAC pair that is valid for shop A's webhook delivery remains a byte-for-byte valid HMAC when replayed with the `shopify-shop-domain` (or `x-shopify-shop-domain`) header swapped to shop B, or with the `shopify-topic` header swapped to a different registered topic. `Utils::HmacValidator.validate` (which only checks `verifiable_query.to_signable_string`, i.e. the body) will still pass: [5](#0-4) 

### Impact Explanation
This is a cross-tenant identity-confusion vector reachable purely from unprivileged HTTP requests to the app's webhook endpoint: an attacker who legitimately receives one authentic webhook delivery for their own store (e.g. by installing the app on a store they control) obtains a valid `(raw_body, hmac)` pair signed with the app's shared secret. They can then submit that same body/HMAC to the app's webhook endpoint with a forged `shopify-shop-domain` header naming a victim shop, and/or a forged `shopify-topic` header naming a different registered topic (e.g. `customers/data_request`, `customers/redact`, `app/uninstalled`). `Registry.process` will accept it as authentic and invoke the app's handler with `WebhookMetadata.shop` set to the victim shop and/or the forged topic, since neither is bound to the signature. This crosses the tenant boundary the gem is meant to enforce and can trigger shop-scoped business logic (data deletion, redaction, uninstall handling, order/inventory side effects) attributed to the wrong tenant.

### Likelihood Explanation
Requires no credentials beyond being able to install the target app on any store (including a free/dev store the attacker controls) to obtain one valid signed webhook body/HMAC pair, then sending a crafted HTTP request with swapped headers to the app's public webhook endpoint. No access token, `client_secret`, or privileged account is needed — only unprivileged interaction with the app as an ordinary merchant/installer plus a forged webhook POST.

### Recommendation
Bind the tenant/topic identity into what is authenticated: include `shop`, `topic`, and `webhook_id` (not just the raw body) in `to_signable_string` for `Webhooks::Request`, or otherwise cryptographically bind those header values to the payload before `Registry.process` trusts them for dispatch and constructs `WebhookMetadata`. At minimum, document and/or provide a mechanism for host apps to cross-check `request.shop` against the shop that has that webhook `topic` currently registered before acting on the payload.

### Proof of Concept
1. Install the target Shopify app on an attacker-controlled store `attacker-shop.myshopify.com` and trigger a webhook delivery for a registered topic, capturing the raw POST body and the `shopify-hmac-sha256` header value sent by Shopify (both valid, since they're signed with the app's real `api_secret_key`).
2. Replay this exact request to the app's webhook endpoint, but replace the `shopify-shop-domain` header with `victim-shop.myshopify.com` (and/or the `shopify-topic` header with a different registered topic string), keeping body and HMAC unchanged.
3. `ShopifyAPI::Utils::HmacValidator.validate` computes the signature only over `raw_body` (`Webhooks::Request#to_signable_string`), so it still matches the unmodified `shopify-hmac-sha256` header.
4. `Webhooks::Registry.process` (lib/shopify_api/webhooks/registry.rb:188-199) dispatches to the handler registered for the (possibly forged) topic with `WebhookMetadata.shop == "victim-shop.myshopify.com"`, even though the payload never actually originated from that shop — demonstrating the cross-tenant identity confusion.

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
