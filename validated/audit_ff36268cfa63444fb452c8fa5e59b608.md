### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body via `Utils::HmacValidator.validate(request)` [1](#0-0) . The `shop` value that is subsequently trusted and handed to the app's webhook handler as the tenant identifier is read from the `shop-domain` header, which is never included in the signed bytes.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [2](#0-1) . The `shop`, `topic`, `api_version`, and `webhook_id` accessors are all pulled from unauthenticated headers: [3](#0-2) .

`HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string`, i.e., the body bytes, and compares it against the received `hmac` header using `OpenSSL.secure_compare` [4](#0-3) . Nowhere in this check is the `shop-domain` header incorporated into the signable string.

`Registry.process` uses this same validated request object to build the `WebhookMetadata` passed to the app's handler, taking `request.shop` verbatim: [1](#0-0) . The gem's own documentation instructs app authors to treat `data.shop` as the authoritative tenant identifier for routing/storing webhook data (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`), i.e. the binding the host app relies on is "HMAC-authenticated request == request.shop" [5](#0-4) .

Because the `api_secret_key`/`client_secret` used to compute the HMAC is a single per-app secret shared across every merchant that has installed the app (not a per-shop secret), any legitimate webhook delivery an attacker receives for their own shop (where the app is installed) is a valid `(raw_body, hmac)` pair under that same app-wide secret. Nothing in `to_signable_string` binds that pair to the originating shop. An attacker can therefore replay that exact body and HMAC while rewriting the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header to any victim shop's domain. `HmacValidator.validate` still succeeds — it only checks the body — and `Registry.process` dispatches the handler with `data.shop` set to the attacker-chosen victim domain, while `data.body` contains attacker-controlled/attacker-owned content.

This breaks the identity binding: "shop domain the request claims to be from" must equal "shop domain the HMAC actually authenticates," but the gem only authenticates the body, not the header.

### Impact Explanation
This is a cross-tenant confusion: the host application, following the gem's documented contract, uses `data.shop` from an HMAC-"validated" webhook to key per-merchant storage, job queues, or business logic. An attacker who is merely an unprivileged merchant with the app installed on their own store can cause fabricated or attacker-influenced webhook payloads to be attributed to an arbitrary other shop, since the gem provides no binding between the authenticated bytes and the shop identity used downstream. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Any entity that can install the app on a shop it controls (a normal, unprivileged action, not requiring any secret or credential belonging to Shopify or another merchant) can capture a valid `(body, hmac)` pair from their own legitimate webhook traffic and replay it with a modified `shop-domain` header to any endpoint the host app exposes for webhook delivery. No `api_secret_key`, access token, or other privileged credential is required — the attacker only needs to be a normal app-installing merchant, satisfying the "unprivileged internet user" constraint.

### Recommendation
Include the shop domain (and ideally topic/webhook id) as part of the signed bytes verified against the request, or independently verify that the `shop-domain` header matches an expected/registered shop for the delivery path before trusting `request.shop` downstream in `ShopifyAPI::Webhooks::Request#shop` / `Registry.process`.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`.
2. Trigger a webhook delivery (e.g. `orders/create`) and capture the raw POST body and its `X-Shopify-Hmac-Sha256` header — this is a valid `(body, hmac)` pair signed with the app's shared `api_secret_key`.
3. Replay this exact request to the app's webhook endpoint, but change `X-Shopify-Shop-Domain` to `victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the (unmodified) body against the HMAC [6](#0-5) .
5. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: <attacker's body>, ...)` [7](#0-6) , causing the host app to process attacker data under the victim shop's tenant context.

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

**File:** docs/usage/webhooks.md (L19-29)
```markdown
```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
