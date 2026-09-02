Based on my investigation, this gem's webhook verification only computes the HMAC over the raw request body, while the `shop` domain that the app relies on to identify the tenant is taken from an HTTP header outside the signed data. This matches the report's bug class ("value that identifies the record acted upon is not bound to the verification that authorizes the action") and satisfies the identity-binding-break criteria for this scan (a field acted on but not covered by the HMAC).

### Title
Webhook shop identity spoofing via unauthenticated header field not covered by HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` (and `topic`, `webhook_id`, `api_version`) values purely from HTTP headers, while `ShopifyAPI::Utils::HmacValidator.validate` (used by `ShopifyAPI::Webhooks::Registry.process`) only verifies the raw request body against the `X-Shopify-Hmac-Sha256` header. The header carrying the shop identity is never part of the signed material, breaking the binding: `hmac_verified(bytes) == shop_trusted(bytes)` does not hold — the gem verifies the body bytes but trusts a separate, unverified header for the tenant identity.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `api_version`, and `webhook_id` accessors are all read straight from HTTP headers, none of which participate in the HMAC computation: [2](#0-1) 

`ShopifyAPI::Webhooks::Registry.process` validates the HMAC (over the body only) and then passes `request.shop` straight into `WebhookMetadata`, which is handed to the app's webhook handler as the authoritative tenant identity: [3](#0-2) 

`ShopifyAPI::Utils::HmacValidator.validate` computes the signature only from `verifiable_query.to_signable_string`, i.e., the raw body in this case, and compares against the caller-supplied `hmac`: [4](#0-3) 

The library's own documentation instructs host apps to trust `data.shop` as "The shop domain of the webhook" and to key business logic on it directly: [5](#0-4) 

Because the webhook HMAC secret (`Context.api_secret_key`) is the app's single `client_secret`, shared across every shop that installs the app — not a per-shop secret — any merchant who has installed the app and can capture one legitimately-signed webhook delivery (a valid `hmac-sha256` header for a given body) can replay that exact HTTP request to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for an arbitrary victim shop. The HMAC still validates (it only checks the body, which is unchanged), and `Registry.process` calls the handler with `WebhookMetadata.shop` set to the attacker-chosen victim domain.

### Impact Explanation
This breaks the identity binding between "who is HMAC-authenticated" and "on whose behalf we act," letting an attacker who controls one shop's webhook deliveries inject arbitrary attacker-controlled payloads into a different shop's tenant context inside the host application. Any app that follows the documented pattern (using `data.shop` to select which tenant's records to mutate, e.g. syncing orders, updating inventory, deleting resources) is exposed to cross-tenant data corruption or unauthorized cross-tenant actions — this is a cross-tenant access vulnerability (Critical, per the given impact scale).

### Likelihood Explanation
Exploitation requires only: (1) the attacker's own shop having installed the app and thus receiving genuinely-HMAC-signed webhook deliveries from Shopify, and (2) the ability to replay an HTTP POST with a modified header to the app's public webhook endpoint — no access token, secret, or privileged account is needed. This is a realistic, low-effort attack path for any unprivileged merchant/tenant of a multi-tenant app built on this gem.

### Recommendation
Bind the shop (and ideally topic/webhook_id/api_version) into the material that is cryptographically verified, or otherwise cross-check the header-derived `shop` against a value obtained through an authenticated channel (e.g., look up the webhook by `webhook_id` against Shopify's API, or maintain a mapping of registered webhook subscriptions per shop and validate that the delivering shop matches an expected identity) before trusting it for tenant-scoped actions. At minimum, document prominently that `data.shop` is not itself HMAC-verified and must not be used as the sole tenant-selection key without additional verification.

### Proof of Concept
1. App installs on `attacker-shop.myshopify.com` and `victim-shop.myshopify.com`, both registered for `orders/create` webhooks to the same app endpoint.
2. Attacker triggers an `orders/create` event on their own shop, Shopify delivers a POST to the app with a valid `X-Shopify-Hmac-Sha256` header computed over the JSON body using the app's shared `client_secret`.
3. Attacker captures this request, changes only the `X-Shopify-Shop-Domain` header to `victim-shop.myshopify.com`, and replays it to the same endpoint.
4. `ShopifyAPI::Webhooks::Request#hmac` still decodes the same valid signature; `Utils::HmacValidator.validate` recomputes HMAC over the unchanged raw body and it matches.
5. `Registry.process` invokes the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, causing the host app to process attacker-controlled order data as if it belonged to the victim shop.

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

**File:** docs/usage/webhooks.md (L12-26)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
```
