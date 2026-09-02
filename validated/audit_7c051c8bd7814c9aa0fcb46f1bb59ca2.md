This confirms the vulnerability: the documentation itself states `ShopifyAPI::Webhooks::Registry.process` will "verify the request did indeed come from Shopify" via HMAC, and the handler receives `data.shop` as the trusted tenant identifier [1](#0-0) , but the HMAC only covers the raw body, not the shop domain.

### Title
Webhook `shop` identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, while `#shop` is read from an unauthenticated HTTP header. `Registry.process` validates the HMAC over the body alone, then passes the unverified `shop` value straight to the app's webhook handler as the tenant identity. Because `shop` is never part of the signed content, any request with a previously-valid (body, HMAC) pair can be replayed with an arbitrary `shop-domain` header and will still pass validation.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` computes the expected signature over `verifiable_query.to_signable_string` and compares it to the received `hmac`: [2](#0-1) 

For webhooks, `to_signable_string` is defined as just the raw request body, while `shop` is read from the `shopify-shop-domain`/`x-shopify-shop-domain` header, entirely outside the signed content: [3](#0-2) 

`Registry.process` validates the HMAC using this body-only signable string, then immediately forwards `request.shop` (still unverified) into `WebhookMetadata`, which the host application's handler is documented to treat as the authoritative shop identity: [4](#0-3) 

The identity binding that should hold is: `shop == the tenant whose data actually produced this HMAC-signed body`. Because `shop` is excluded from `to_signable_string`, this equality is never checked — the gem verifies "this body was signed with our app secret" but not "this body belongs to this shop." Since Shopify signs all webhooks for an app with the same `api_secret_key` regardless of which shop triggered the event, any (body, hmac) pair captured from one shop's webhook remains valid when replayed with a forged `shop-domain` header claiming to belong to a different shop that has also installed the app. An attacker who installs the app on a shop they control can trigger a webhook, capture the body+HMAC (or send an equivalent payload/HMAC pair by legitimate means), then POST it directly to the app's public webhook endpoint with the `shop-domain` header set to a victim shop, bypassing Shopify's delivery infrastructure entirely.

### Impact Explanation
This breaks the tenant boundary the gem is documented to enforce ("verify the request did indeed come from Shopify") [5](#0-4) . A host application relying on `data.shop` from `WebhookMetadata` to scope which merchant's records to create/update/delete (the gem's own documented usage pattern) [6](#0-5)  can be made to attribute attacker-controlled webhook content to an arbitrary victim shop, i.e. cross-tenant data injection through the gem's own HMAC "verification" API.

### Likelihood Explanation
Exploitation requires only: (1) the attacker's own shop installs the target app (a routine, low-privilege action for any public app), (2) the attacker triggers a normal webhook event on their own shop and captures the body/HMAC pair, and (3) the attacker sends a raw HTTP POST directly to the app's public webhook endpoint with a forged `shop-domain` header. No access token, `client_secret`, or Shopify infrastructure access is needed — the endpoint is public by design.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) in the value that is cryptographically bound and checked, or otherwise require the `Request#shop` value to be independently verified against the request context (e.g., cross-check against an expected shop for the endpoint, or bind shop into `to_signable_string` if Shopify's signing scheme supports it). At minimum, document prominently that `data.shop` is unauthenticated and must not be trusted for tenant scoping without additional verification, since the current `Registry.process` and docs imply it has already been validated.

### Proof of Concept
```ruby
# Attacker controls "attacker-shop.myshopify.com" and has installed the target app on it.
# Step 1: Attacker triggers a real webhook (e.g. orders/create) on their own shop and
# captures the raw POST body + "X-Shopify-Hmac-Sha256" header from their own server logs/proxy.
captured_body = '{"id":1,"note":"pwned"}'
captured_hmac_b64 = "<hmac captured from Shopify's legitimate delivery to attacker's own shop>"

# Step 2: Attacker replays the exact same body+hmac directly to the app's public
# webhook endpoint, but swaps the shop-domain header to the victim shop.
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => captured_hmac_b64,
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged, not covered by HMAC
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: captured_body, headers: headers)

# Step 3: Registry.process validates fine, because HmacValidator only checks
# HMAC(raw_body) against the shared app secret — `shop` is never part of the signature.
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle(data: WebhookMetadata(shop: "victim-shop.myshopify.com", body: {"id"=>1,"note"=>"pwned"}, ...))
# The host app now believes attacker-controlled data belongs to victim-shop.
```

### Citations

**File:** docs/usage/webhooks.md (L10-16)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
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

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
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
