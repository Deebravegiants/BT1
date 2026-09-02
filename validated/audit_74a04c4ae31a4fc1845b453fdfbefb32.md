### Title
Webhook `shop` (and `topic`/`webhook_id`) header is trusted for tenant identification without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/registry.rb`, `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as verified once the HMAC check passes, then hands the handler a `WebhookMetadata` built from unauthenticated headers, including `shop`. But the HMAC signature only ever covers the raw request body, not the `shopify-shop-domain`, `shopify-topic`, or `shopify-webhook-id` headers. This breaks the identity binding `HMAC-verified bytes == bytes acted upon`, since the tenant identity (`shop`) used by the caller's handler is a value that was never part of what was cryptographically verified.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are all read straight from HTTP headers with no cryptographic binding to the signed body: [2](#0-1) 

`Registry.process` validates the HMAC (which only covers `@raw_body`) and then immediately trusts `request.shop` (and `request.topic`, `request.webhook_id`) to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` only ever hashes `verifiable_query.to_signable_string`, i.e., the body — never the headers: [4](#0-3) 

The gem's own documentation instructs app authors to use `data.shop` directly as the tenant key (e.g., for job routing/storage), reinforcing that this field is expected to be trustworthy once `Registry.process` succeeds: [5](#0-4) [6](#0-5) 

Because `Context.api_secret_key` is a single shared secret for the whole app (not per-shop), any unprivileged user who installs the app on their own store legitimately receives real Shopify webhook deliveries with valid `(body, hmac)` pairs signed with that same shared secret. That attacker can then replay the exact same body/HMAC to the app's webhook endpoint while substituting the `shopify-shop-domain` (and `shopify-topic`/`shopify-webhook-id`) headers to any value they choose. `HmacValidator.validate` still returns `true` because the signature check never touches those headers, yet `Registry.process` will invoke the handler with `WebhookMetadata#shop` set to the attacker-chosen (potentially victim) shop domain.

Binding that should hold: `hmac_verified_bytes == bytes_that_determine_tenant_identity`. In this code, `hmac_verified_bytes = raw_body` while `tenant_identity = header["shopify-shop-domain"]`, which are disjoint — the equality does not hold.

### Impact Explanation
Any app built with this gem that uses `WebhookMetadata#shop` (as documented) to select which tenant's data/session/queue to act on can be made to process attacker-supplied body content under an arbitrary victim shop's identity. This is a cross-tenant identity-confusion primitive delivered entirely through the gem's documented webhook-processing API (`Registry.process` + `Request`), not through host-application misuse of an undocumented API — the docs explicitly recommend using `data.shop` this way.

### Likelihood Explanation
Any user can freely install a public/free instance of the target Shopify app on their own store, which causes Shopify to send them real webhook deliveries signed with the app's single shared secret. Capturing a `(raw_body, hmac header)` pair from their own legitimate webhook traffic and replaying it against the same public webhook endpoint with a modified `shopify-shop-domain` header requires no special access, no leaked credentials, and no privileged account — only normal use of the app as an unprivileged merchant/tenant.

### Recommendation
Bind the tenant/topic identity into the value that is HMAC-verified: derive `shop`/`topic`/`webhook_id` from a signed source (e.g., include them as part of the signable string alongside the body, or perform an authenticated lookup of the shop that corresponds to the resource ids embedded in the JSON body) rather than trusting bare HTTP headers once only the body’s HMAC has been checked.

### Proof of Concept
1. Attacker installs the target app on their own development store (`attacker.myshopify.com`) and triggers a webhook (e.g., `orders/create`). Shopify delivers:
   - Headers: `shopify-topic: orders/create`, `shopify-shop-domain: attacker.myshopify.com`, `shopify-hmac-sha256: <valid HMAC over body>`
   - Body: `{"id":1,...attacker-controlled order fields...}`
2. Attacker resends the exact same body and `shopify-hmac-sha256` value to the app's webhook endpoint, but rewrites `shopify-shop-domain: victim.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `@raw_body` — unchanged from step 1 — so validation succeeds: [3](#0-2) [7](#0-6) 
4. The handler is invoked with `WebhookMetadata.new(..., shop: "victim.myshopify.com", body: <attacker-controlled JSON>, ...)`, causing the app to attribute attacker-controlled webhook content to the victim tenant.

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

**File:** docs/usage/webhooks.md (L10-30)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

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
    end
  end
end
```
```

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
