### Title
Webhook `shop`, `topic`, `webhook-id` and `api-version` identifiers are not covered by the HMAC signature, enabling tenant-identity spoofing on webhook replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, while the `shop`, `topic`, `webhook-id`, and `api-version` values used to identify the tenant and route the event to the handler are taken from unauthenticated HTTP headers that are never included in the signed payload.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 
while `shop`, `topic`, `webhook_id`, and `api_version` are all read from HTTP headers that are outside the HMAC's coverage: [2](#0-1) 

`Registry.process` validates only this body-only HMAC, then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` from headers to build the data handed to the app's handler: [3](#0-2) 

The identity binding that should hold is:
`HMAC-covered bytes == bytes that determine which shop/topic/webhook the event is attributed to`

In this implementation that equality does not hold: `HMAC(raw_body, secret)` only binds the JSON body; it does not bind the `shop-domain`, `topic`, `webhook-id`, or `api-version` headers. As documented, app developers are expected to trust `data.shop` as "The shop domain of the webhook" and use it directly to route/attribute the event: [4](#0-3) 

Because the signature only proves "this body was HMAC'd with the app's secret at some point," not "this body was HMAC'd *for this shop/topic*," a valid `(raw_body, hmac)` pair legitimately obtained for one webhook delivery can be resubmitted to the app's webhook endpoint with the `shop-domain` (and/or `topic`/`webhook-id`) header swapped to a different, victim shop's domain. The `HmacValidator.validate` call still succeeds because it only recomputes and compares the digest of the untouched body: [5](#0-4) 

The app's handler then processes the (unmodified, genuinely signed) body as if it belonged to the attacker-chosen `shop`, `topic`, and `webhook_id`, since these are read straight from `WebhookMetadata` built from the unauthenticated headers.

### Impact Explanation
This breaks the single-tenant isolation guarantee webhook processing is supposed to provide: an unprivileged party who can obtain any one legitimate `(raw_body, hmac)` pair for the app (e.g., by triggering an event in their own connected shop and capturing the resulting webhook) can replay it against the same public endpoint with a different `x-shopify-shop-domain`/`topic`/`webhook-id` header. Any app logic that trusts `data.shop` to select which tenant's records to create/update/delete (the exact pattern shown in the gem's own documentation) can be tricked into applying another shop's webhook body to the wrong tenant, or vice versa — a cross-tenant data-integrity/isolation violation. This matches the "Critical - cross-tenant access" impact category, since it lets one tenant's traffic be attributed to (and acted upon) another tenant without any credential belonging to that tenant.

### Likelihood Explanation
The webhook endpoint is a public HTTP route by design (it must be reachable by Shopify), so no privileged access, TLS interception, or leaked secret is required. The only prerequisite is a single legitimate webhook delivery, which any developer/attacker with their own connected shop can trivially obtain by causing a real event (e.g., `orders/create`) to fire against their own install, then replaying the captured body+HMAC with altered identity headers. This requires no knowledge of `api_secret_key` or any access token, and only interaction with the app's own publicly exposed webhook callback.

### Recommendation
Include the identifying fields (`shop`, `topic`, `webhook_id`, `api_version`) in the signed payload used for HMAC verification (or otherwise cryptographically bind them to the body, e.g. compute the HMAC over a canonical string containing both headers and body), so that swapping any of these headers invalidates the signature. Alternatively, cross-check the header-derived `shop` against a shop identifier embedded inside the verified JSON body before dispatching to the handler.

### Proof of Concept
1. App installs the webhook handler and registers `orders/create` per the documented pattern in `docs/usage/webhooks.md`.
2. Attacker's own shop `attacker-shop.myshopify.com` is connected to the app; attacker creates an order, causing Shopify to send a legitimate webhook: headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: <valid HMAC of raw_body>`, plus `raw_body`.
3. Attacker captures this raw request (body + hmac header), and resends it to the same app endpoint but with `x-shopify-shop-domain` changed to `victim-shop.myshopify.com` (body and hmac header untouched).
4. `ShopifyAPI::Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` recomputes the HMAC over the unchanged `raw_body` and it matches — validation succeeds.
5. `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) builds `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and dispatches to the handler, which — per the documented usage pattern — acts on `victim-shop.myshopify.com` using data that actually belongs to `attacker-shop.myshopify.com`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
