### Title
Webhook shop domain and topic are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable payload from the raw body only, while the `shop`, `topic`, `webhook_id`, and `api_version` fields that are subsequently trusted by `ShopifyAPI::Webhooks::Registry.process` are read directly from unauthenticated HTTP headers. Because the HMAC never binds these header values, an attacker who can obtain any valid `(body, hmac)` pair for the app's shared `api_secret_key` can replay it with a forged `shop-domain` header to make the app process attacker-chosen webhook data as if it came from a different, victim shop.

### Finding Description
`HmacValidator.validate` verifies the payload by recomputing the HMAC over `verifiable_query.to_signable_string` and comparing it against `verifiable_query.hmac`: [1](#0-0) 

For webhook requests, `to_signable_string` is defined to return only the raw request body — none of the Shopify-supplied headers are included in the signed material: [2](#0-1) 

Meanwhile, `shop`, `topic`, `webhook_id`, and `api_version` are all parsed straight from headers that are not part of the HMAC computation: [3](#0-2) 

`Registry.process` validates the HMAC and then dispatches to the app handler using these unauthenticated fields verbatim: [4](#0-3) 

This breaks the identity binding the report's bug-class describes: the equality that should hold is `shop_authenticated_by_hmac == shop_acted_on`, but here the HMAC authenticates only the body, so effectively `shop_authenticated_by_hmac == "" (nothing)` while `shop_acted_on == header["shopify-shop-domain"]` (attacker-controlled). Any valid `(body, hmac)` pair — for example one captured from a legitimate webhook delivered to the attacker's own store/installation, or one with a predictable/empty body shared across all shops (as shown in the test fixtures using body `"{}"`) — remains valid under `HmacValidator.validate` regardless of which shop domain, topic, webhook ID, or API version header is attached to it.

### Impact Explanation
An unprivileged merchant who has the app installed on their own store receives webhook deliveries with a valid HMAC computed only over the body, using the app's shared `api_secret_key` (not tied to their particular shop). By replaying that `(body, hmac)` pair to the app's webhook callback endpoint while substituting the `shopify-shop-domain` header for a victim shop's domain (and optionally a different `topic`), the attacker causes `ShopifyAPI::Webhooks::Registry.process` to invoke the app's handler with `WebhookMetadata` claiming the data originated from the victim shop. Any host application that uses `data.shop` from the gem's `WebhookMetadata` as the tenant key (which is exactly the pattern the gem's own documentation recommends) will attribute attacker-controlled webhook data to another tenant, resulting in cross-tenant data injection/corruption.

### Likelihood Explanation
Exploitation requires only the ability to send an HTTP request with a copied `hmac` header and a modified `shop-domain` header — no access to `api_secret_key`, access tokens, or privileged credentials is needed, satisfying the "unprivileged internet user" bar. Obtaining at least one valid `(body, hmac)` pair is straightforward since the attacker can install the app on a shop they control and observe a real webhook delivery (bodies for certain topics, like `app/uninstalled`, are also often minimal/predictable).

### Recommendation
Include the shop domain (and ideally topic/webhook id/api version) in the HMAC-signable string for webhook requests, or otherwise cryptographically bind these header values to the signature, so that `HmacValidator.validate` fails if any of them are altered relative to what Shopify originally signed for. Alternatively, document explicitly and enforce within the gem that `data.shop` must be cross-checked by the host application against the shop that owns the specific webhook subscription/ID before being trusted as a tenant identifier.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and lets it register for a webhook topic with a small/predictable body (e.g. `app/uninstalled`, or any topic where the body content is attacker-influenced, such as updating a product they own).
2. Attacker captures the resulting webhook HTTP request, including the `shopify-hmac-sha256` header and raw body.
3. Attacker resends the same body and `hmac` header to the app's webhook endpoint, but sets `shopify-shop-domain: victim-shop.myshopify.com` (and optionally a different `shopify-topic`).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because the HMAC only ever covered the (unchanged) body: [4](#0-3) 
5. The registered handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"`, and the host app processes/stores attacker-controlled data under the victim's tenant identity.

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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
