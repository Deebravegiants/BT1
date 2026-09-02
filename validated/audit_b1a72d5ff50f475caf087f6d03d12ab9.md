### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from the `x-shopify-shop-domain` / `shopify-shop-domain` HTTP header, but the HMAC signature that `Registry.process` verifies is computed only over the raw request body. Because the `shop` field used to route/attribute the webhook is not part of the signed material, an attacker who possesses one valid `(body, hmac)` pair — trivially obtainable by triggering a real webhook to their own shop's registered endpoint — can replay that exact body/HMAC to the target app while substituting an arbitrary `shop-domain` header. The signature still validates, but the webhook is now attributed to a victim tenant chosen by the attacker.

### Finding Description
`Registry.process` validates a webhook exclusively via: [1](#0-0) 

The HMAC check calls `Utils::HmacValidator.validate(request)`, which computes the signature over `request.to_signable_string`: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns only the raw body — none of the identifying headers (topic, shop-domain, webhook-id, api-version) are included in the signed string: [3](#0-2) 

Yet `shop` (parsed straight from the unauthenticated header) is exactly the field passed to the application's handler as the tenant identifier: [4](#0-3) 

This breaks the intended binding: `shop-that-produced-and-signed-the-body == shop-attributed-to-the-webhook-event`. Since the header is excluded from the signable string, an attacker can present `shop = other_shop_that_produced_and_signed_the_body` while keeping the body+HMAC from a webhook they legitimately received for their own store (which they can generate at will, e.g. by placing a test order, updating a product, etc. on their own installed shop). The documented handler contract explicitly trusts `data.shop` as the shop the event came from: [5](#0-4) 

### Impact Explanation
Any app built on this gem that keys business logic, database writes, session/token lookups, or job dispatch off `WebhookMetadata#shop` (exactly the pattern shown in the gem's own documentation, `perform_later(topic:, shop_domain: data.shop, ...)`) can be made to process attacker-controlled webhook bodies under a victim shop's identity. This is a cross-tenant confusion: data belonging to one merchant can be injected/attributed to another merchant's tenant record without ever needing that merchant's credentials, satisfying the "cross-tenant access" criterion.

### Likelihood Explanation
The prerequisite — obtaining one valid `(raw_body, hmac)` pair — is trivial for any developer with their own Shopify development store: they simply install their own app, register a webhook, and capture the resulting POST, which they are fully authorized to generate. No secret material or victim credentials are required to then forge the target shop attribution, only the ability to POST directly to the app's public webhook endpoint with a spoofed `shopify-shop-domain` header.

### Recommendation
Include the identifying headers (`shop-domain`, `topic`, `webhook_id`, `api_version`) in the signed material used for verification, or otherwise cryptographically bind the shop to the payload — e.g. reconstruct `to_signable_string` to concatenate the canonical headers with the raw body before hashing, matching what is actually authenticated. Alternatively, the gem should document to consumers that `data.shop` is not authenticated and must be cross-checked against the shop associated with the specific `webhook_id`/subscription registered via the GraphQL API, rather than trusted directly for tenant routing.

### Proof of Concept
1. Attacker owns/operates `attacker-shop.myshopify.com`, installs the target app, and registers webhook topic `orders/create`.
2. Attacker triggers an order creation on their own shop, capturing Shopify's real POST: raw body `B` and header `x-shopify-hmac-sha256: H` (valid because Shopify itself signed `B` with the app's `client_secret`).
3. Attacker sends a new POST to the same app webhook endpoint with:
   - body = `B` (unchanged)
   - header `x-shopify-hmac-sha256: H` (unchanged)
   - header `x-shopify-shop-domain: victim-shop.myshopify.com` (spoofed)
   - header `x-shopify-topic: orders/create` (unchanged)
4. `Registry.process` calls `HmacValidator.validate`, which recomputes the HMAC over `@raw_body` only (`to_signable_string`) — matches `H` — validation succeeds.
5. The app's handler receives `WebhookMetadata(shop: "victim-shop.myshopify.com", body: B, ...)` and performs tenant-scoped work (e.g., enqueues a job, writes to victim's DB row) using attacker-controlled data, despite the victim shop never sending this event.

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

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** docs/usage/webhooks.md (L10-18)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```
