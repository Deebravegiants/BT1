## Title
Webhook shop-domain header is trusted without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating an HMAC computed **only over the raw request body**, but the `shop` value that the host application uses to attribute the event to a tenant is read from an HTTP header that is never included in that signed payload. Any actor who can generate a validly-signed webhook for their own shop (installing the app is enough — no `api_secret_key`, access token, or privileged account required) can replay that exact body with a forged `shop-domain` header pointing at a victim shop, and the gem will report the webhook as valid and originating from the victim.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`shop` is read straight from an attacker-controllable header, with no cryptographic binding to the body or the HMAC: [2](#0-1) 

`Utils::HmacValidator.validate_signature` computes the signature strictly over `verifiable_query.to_signable_string` (i.e. the raw body) and compares it against the received `hmac`: [3](#0-2) 

`Registry.process` validates only that HMAC, then forwards `request.shop` — the unauthenticated header — directly to the app's handler as the tenant identifier: [4](#0-3) 

Because the `api_secret_key` is the same for every shop that installs a given app (it's an app-level secret, not a per-shop one), a signature that is valid for one shop's webhook body is valid for the same body under **any** shop header. The identity binding that should hold — `shop asserted in the HMAC-signed payload == shop delivered to the handler` — is broken: the gem only proves "this body was HMAC-signed with our app secret," not "this body was sent about this shop." The documentation reinforces that host apps are meant to trust the verified/parsed data as a package, describing `process` as verifying "the request did indeed come from Shopify" and `data.shop` as "The shop domain of the webhook": [5](#0-4) [6](#0-5) 

### Impact Explanation
An unprivileged actor (anyone able to install the app on a shop they control, e.g. a free development store) can:
1. Trigger a real webhook event on their own shop, capturing the raw body and its valid `X-Shopify-Hmac-Sha256` value.
2. Replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain.
3. `Registry.process` validates the (unchanged, still-valid) HMAC and dispatches the handler with `WebhookMetadata#shop` set to the victim's domain.

Any host application that keys off `data.shop` to select the tenant record to update (the pattern the gem's own docs demonstrate) will apply attacker-controlled webhook content to the wrong tenant — a cross-tenant data-integrity/confidentiality break requiring no secrets, tokens, or elevated privileges.

### Likelihood Explanation
High for apps distributed publicly: obtaining a legitimate signed webhook only requires installing the app on any shop (including one the attacker controls) and triggering a supported event, then a simple HTTP replay with a modified header.

### Recommendation
Bind the header-derived identity to the signed payload before trusting it — e.g., include `shop-domain` (and `topic`, `webhook-id`) in the bytes covered by the HMAC (as Shopify's newer webhook formats already carry these in signable metadata), or independently verify that the `shop` header corresponds to a shop with an active installation/session known to the app before dispatching to handlers, rather than treating the header as authenticated once the body-only HMAC passes.

### Proof of Concept
```ruby
# Attacker owns/installs the app on attacker-shop.myshopify.com and triggers "orders/create".
# They capture the real webhook delivery:
raw_body = '{"id":1,"note":"hello"}'
valid_hmac = Base64.encode64(
  OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body)
)

# Replay with a forged shop header pointing at the victim:
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => valid_hmac,       # unchanged, still valid — HMAC never covered shop
  "x-shopify-shop-domain" => "victim-shop.myshopify.com",
}

req = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(req)
# Handler receives WebhookMetadata(shop: "victim-shop.myshopify.com", body: {...})
# even though the event never occurred on victim-shop.
```

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```

**File:** docs/usage/webhooks.md (L123-135)
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
