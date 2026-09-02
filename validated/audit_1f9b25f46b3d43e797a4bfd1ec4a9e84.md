This confirms the finding: the docs explicitly promise `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify" (docs/usage/webhooks.md line 125), and the gem passes `data.shop` straight to the app's handler as the tenant identifier (docs/usage/webhooks.md lines 13-14, 25-26), but the HMAC only ever covers the raw body, never the `shop-domain` header.### Title
Webhook Shop Identity Not Bound to HMAC Signature Enables Cross-Tenant Webhook Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely by checking the HMAC over the raw request body, then hands the handler a `shop` value taken from the `X-Shopify-Shop-Domain` header — a field that is never included in the signed bytes. An attacker who can obtain one genuinely Shopify-signed webhook body (e.g., by owning/controlling their own shop, which is unprivileged) can replay that exact body with a forged `shop-domain` header pointing at a victim shop, and the gem will report it as valid and authoritative for the victim tenant.

### Finding Description
`Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` and compares it to the received signature [1](#0-0) . For webhooks, `Webhooks::Request#to_signable_string` returns only `@raw_body` [2](#0-1) , while `Request#shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header without any cryptographic binding to the body or signature [3](#0-2) .

`Registry.process` only checks `Utils::HmacValidator.validate(request)` before dispatching to the handler, and then constructs `WebhookMetadata` using `request.shop` taken straight from the unauthenticated header: [4](#0-3) .

The documentation explicitly tells integrators that `Registry.process` "will verify the request did indeed come from Shopify" and that the resulting `data.shop` is "The shop domain of the webhook," to be trusted and used directly for tenant routing (e.g., `perform_later(topic: data.topic, shop_domain: data.shop, ...)`) [5](#0-4) . This creates an identity-binding mismatch: the shop that is *authenticated* (none — the header is unsigned) is not the shop that is *acted upon* (the header value trusted by the app via the gem's documented API).

Because a `myshopify.com` store owner is an unprivileged party with respect to another merchant's tenant, this owner can:
1. Install the victim app on their own shop and receive a legitimate Shopify-signed webhook (valid HMAC computed with the app's real `client_secret` over the raw body).
2. Replay the identical raw body and HMAC header to the app's public webhook endpoint, but substitute the `X-Shopify-Shop-Domain` header with the victim's shop domain.
3. `HmacValidator.validate` still passes (it only checks the body), and `Registry.process` invokes the app's handler with `shop` set to the attacker-chosen victim domain.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook processing (cross-tenant access), since the handler receives attacker-controlled `shop` values believed to be Shopify-authenticated. Depending on how the host app uses `data.shop` (e.g., to look up which merchant's session/access token to act on, or to write attacker-supplied `body` content into a specific merchant's records), this can lead to data being attributed to or applied against the wrong merchant — a cross-tenant integrity/confidentiality violation stemming directly from this gem's webhook verification contract.

### Likelihood Explanation
Exploitation only requires the ability to install the target app on any shop (or otherwise obtain one valid signed webhook payload) and the ability to send arbitrary HTTP requests to the app's public webhook endpoint with custom headers — both are available to an ordinary, unprivileged internet user/merchant, with no access token, secret, or privileged account needed.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) header values into the signed material, or otherwise fail closed unless the shop is corroborated against a value cryptographically tied to the HMAC (e.g., include the header values in `to_signable_string`, or require the host application to look up an existing session for the claimed shop and reject unknown/mismatched shops before trusting `WebhookMetadata#shop`). At minimum, update `Webhooks::Request#to_signable_string` to incorporate the shop-domain header in the signable string so that a mismatched shop invalidates the HMAC.

### Proof of Concept
```ruby
# Attacker installs the app on their own shop "attacker.myshopify.com"
# and captures one genuine Shopify webhook: raw_body + valid HMAC header.

raw_body = '{"id":1,"note":"hello"}'
valid_hmac = "<hmac Shopify computed for attacker's shop>"  # signed w/ app's real client_secret

# Attacker now POSTs the same body+hmac to the app's webhook endpoint,
# but swaps the shop-domain header to the victim's shop:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => valid_hmac,
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged, unsigned
  "x-shopify-webhook-id" => "any-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate passes (only body is checked)
# => handler.handle receives WebhookMetadata with shop: "victim-shop.myshopify.com"
```

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
