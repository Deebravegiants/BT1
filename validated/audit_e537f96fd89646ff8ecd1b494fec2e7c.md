### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing tenant confusion between HMAC-authenticated payload and shop identity - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` signs and verifies only the raw JSON body via HMAC, while the `shop` (from the `X-Shopify-Shop-Domain` header) that identifies the tenant is read separately and never included in the signed content. `Registry.process` validates the HMAC over the body only, then trusts the unauthenticated `shop` header as the tenant identity handed to the app's webhook handler. This is the same class of bug as the reported `EVToken` issue: a value that is exposed/consumed by the calling code (`_opt.fee` / here, `data.shop`) is not the value that participates in the integrity check (`bytesNeeded(fee)` stored in `constructor` bytecode / here, `to_signable_string` = `@raw_body` only), creating a discrepancy between what's verified and what's acted upon.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Webhooks::Request#shop` reads the `shop-domain` header independently, and is never mixed into `to_signable_string`: [2](#0-1) 

`HmacValidator.validate` only checks `verifiable_query.hmac` against `verifiable_query.to_signable_string`: [3](#0-2) 

`Registry.process` validates the HMAC (over body only), then constructs `WebhookMetadata` using `request.shop`, which is passed to the application's handler as the trusted tenant identifier, without any additional check that the shop is bound to the signed body: [4](#0-3) 

The identity binding that should hold is: `shop header == shop covered by HMAC`. Because the HMAC secret (`api_secret_key`) is shared across all shops of an app, any request with a valid `(raw_body, hmac)` pair — for example a legitimate webhook the attacker received for their *own* installed shop — remains HMAC-valid no matter what `shop-domain` header value accompanies it. An attacker who controls one shop that has installed the app can capture a real webhook delivery (body + valid HMAC) and replay it to the app's webhook endpoint with an arbitrary `X-Shopify-Shop-Domain` header (e.g., a victim shop). `Registry.process` will accept it as authentic and hand the handler `WebhookMetadata.shop = <victim shop>` together with the attacker's own webhook body, exactly as documented in `docs/usage/webhooks.md`: [5](#0-4) 

This lets the attacker inject data attributed to any shop tenant into the host application's webhook processing pipeline (e.g., `perform_later(shop_domain: data.shop, webhook: data.body)`), since the gem gives no cryptographic assurance that the `shop` value is bound to the verified body.

### Impact Explanation
This breaks the tenant-identity binding the HMAC is meant to provide, allowing cross-tenant data injection: the application ends up processing attacker-supplied webhook content while attributing it to a shop the attacker does not control, without the app having any way to detect the mismatch (since the gem itself never checks shop-vs-signature binding). This matches the Critical "cross-tenant access" impact category, since an unprivileged merchant/attacker can make requests appear to originate from a shop that is not their own.

### Likelihood Explanation
Likelihood is Medium: it requires the attacker to (1) install the vulnerable app on their own store to receive at least one legitimate webhook with a valid HMAC, and (2) know or guess a target shop's domain to place in the spoofed header — both of which are realistic for any public Shopify app, and neither requires any secret or privileged credential.

### Recommendation
Include the shop domain (and ideally the topic/webhook id) in the HMAC-covered content for webhooks, or otherwise cryptographically bind `shop` to the verified payload before it is handed to `WebhookMetadata`/application handlers, so that `Utils::HmacValidator.validate` fails whenever the `shop-domain` header does not match the shop the payload was actually generated for.

### Proof of Concept
```ruby
# Attacker installs the app on their own shop "attacker.myshopify.com"
# and captures a real, valid webhook delivery:
raw_body = '{"id":1,"note":"hello"}'
valid_hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body)

# Attacker replays the SAME body+hmac but swaps the shop-domain header
# to point at a victim shop they do not control:
spoofed_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(valid_hmac),
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # not the attacker's shop
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: spoofed_headers)

# HMAC validation succeeds (only raw_body is checked), and the handler
# receives WebhookMetadata.shop == "victim-shop.myshopify.com"
ShopifyAPI::Webhooks::Registry.process(request)
```
`Registry.process` and `HmacValidator.validate` never reject this because `shop` is not part of `to_signable_string`: [6](#0-5) [1](#0-0)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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

**File:** docs/usage/webhooks.md (L8-30)
```markdown
## Create a Webhook Handler

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
