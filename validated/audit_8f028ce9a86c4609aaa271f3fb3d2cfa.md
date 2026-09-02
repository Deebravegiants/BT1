### Title
Webhook `shop` identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` is documented as verifying "the request did indeed come from Shopify" before invoking the app's handler with a `WebhookMetadata` object that includes the `shop` domain. In reality, the HMAC only authenticates the raw request body — the `shop-domain` header used to identify the tenant is never included in the signed bytes, so any holder of a valid `(body, hmac)` pair for the shared app secret can attach an arbitrary `shop` value and have it accepted as authentic.

### Finding Description
The identity binding that should hold is:
`shop_header_trusted_by_handler == shop_that_actually_produced_the_signed_body`

In `lib/shopify_api/webhooks/request.rb`, the HMAC is computed only from the raw body: [1](#0-0) [2](#0-1) 

while `shop` is read straight from an unauthenticated header, unrelated to `to_signable_string`: [3](#0-2) 

`Registry.process` validates the HMAC and then forwards `request.shop` straight to the app's handler without any cross-check that this shop actually produced the signed body: [4](#0-3) 

Since a single app-level `client_secret` (`Context.api_secret_key`) is used to compute/verify the HMAC for *every* installed shop (see `HmacValidator.validate_signature` / `compute_signature`): [5](#0-4) 

any shop that has legitimately installed the app can generate a genuinely-signed `(body, hmac)` pair for itself (e.g., by triggering a real event, or by using its own real webhook deliveries), then replay that exact body/HMAC pair to the app's webhook endpoint while swapping the `X-Shopify-Shop-Domain` header to a victim shop's domain. `Utils::HmacValidator.validate` will report success because it only checks the body bytes against the shared secret — it never checks that the presented `shop` corresponds to the signer: [6](#0-5) 

The gem's own documentation reinforces the false assumption that `data.shop` is trustworthy once `process` succeeds: [7](#0-6) [8](#0-7) 

### Impact Explanation
This breaks the tenant boundary the gem claims to enforce: an attacker who is a legitimate merchant of the app can forge webhook deliveries that are accepted as authentic for a different, victim shop. Any host application that follows the documented pattern of trusting `data.shop` from `WebhookMetadata` (as the docs explicitly instruct) to attribute webhook data/actions to a shop record will process attacker-controlled data under another tenant's identity — a cross-tenant data injection into another merchant's data (e.g., poisoning inventory, order, or customer webhook processing for a shop the attacker doesn't control). This matches the "cross-tenant access" Critical-impact category.

### Likelihood Explanation
Exploitation requires only that the attacker control one shop that installs the target app (a normal, unprivileged capability — any Shopify merchant can install a public app), capture a validly-signed webhook body/HMAC pair sent to their own store, and replay it to the app's public webhook endpoint with a modified `shop-domain` header. No access token, `client_secret`, or privileged account is required; the `client_secret` is only used internally by the gem to verify, never disclosed to the attacker. This is a realistic, no-special-access attack path.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the HMAC-verified data, or independently authenticate the `X-Shopify-Shop-Domain` header against a known/registered shop record before trusting it, rather than exposing it unauthenticated in `WebhookMetadata`. At minimum, the gem's documentation should not claim `process` "verifies the request did indeed come from Shopify" for the `shop` field when that field is excluded from the signed bytes.

### Proof of Concept
```ruby
# Attacker owns "attacker-shop.myshopify.com" and has installed the target app.
# Shopify sends the attacker a legitimately signed webhook for their own shop:
body = '{"id":1,"note":"legit change on attacker shop"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), app_client_secret, body)

# Attacker replays the exact same body+hmac to the app's public webhook endpoint,
# but swaps the shop-domain header to a victim shop they do not control:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged
  "x-shopify-webhook-id" => "forged-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HMAC check passes (only body is verified), handler receives
#    data.shop == "victim-shop.myshopify.com" even though victim-shop never sent this webhook.
```

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-40)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end

        sig { params(signable_string: String, secret: String).returns(String) }
        def compute_signature(signable_string, secret)
          OpenSSL::HMAC.hexdigest(
            OpenSSL::Digest.new("sha256"),
            secret,
            signable_string,
          )
        end
```

**File:** docs/usage/webhooks.md (L12-18)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```

**File:** docs/usage/webhooks.md (L123-136)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```ruby
class WebhookController < ApplicationController
  def webhook
    ShopifyAPI::Webhooks::Registry.process(
      ShopifyAPI::Webhooks::Request.new(raw_body: request.raw_post, headers: request.headers.to_h)
    )
    render json: {success: true}.to_json
  end
end
```
```
