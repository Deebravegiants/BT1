### Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant webhook replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes and verifies the webhook HMAC over the raw body only, while the `shop-domain` header (used by the gem to identify which tenant/shop the webhook belongs to) is completely excluded from the signed material. This is the exact bug class from the report: a field that is *acted upon* (`request.shop`, which downstream is treated as the source-of-truth tenant identifier passed to the app's handler) is not covered by the HMAC that is supposed to authenticate the whole request.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`ShopifyAPI::Webhooks::Registry.process` validates the request using `Utils::HmacValidator.validate(request)`, which signs/verifies exactly that `to_signable_string` value (the raw body) with `Context.api_secret_key`: [2](#0-1) [3](#0-2) 

The `shop` value read from the `x-shopify-shop-domain` / `shopify-shop-domain` header is never part of the signed string: [4](#0-3) 

Yet `shop` is exactly the field the gem hands to the host application's handler as the tenant identity for the webhook, per the documented contract (`data.shop`): [5](#0-4) [6](#0-5) 

**Binding that should hold:** `hmac == HMAC(secret, body || shop || topic)` (or otherwise the shop must be independently trusted). What actually holds: `hmac == HMAC(secret, body)`, with `shop` supplied unauthenticated. Because `api_secret_key` is a single **per-app** secret (not per-shop), any valid `(raw_body, hmac)` pair the app has ever legitimately received for *any* installed shop — including the attacker's own store, where the attacker fully controls the webhook payload content and can capture a genuine `hmac` for it from Shopify — remains a **valid signature regardless of which shop-domain header is attached to it**. An attacker who has installed the app on their own shop can:
1. Trigger a webhook to their own shop and capture the raw body + valid `hmac-sha256` header Shopify sent (both derived from the shared `api_secret_key`).
2. Replay that exact `(raw_body, hmac)` pair to the app's webhook endpoint, but substitute `shopify-shop-domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` only checks the body's HMAC (unaffected by the header change), so validation passes, and the handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker-controlled body>, ...)`.

### Impact Explanation
This breaks the tenant/shop authentication boundary: the gem hands the host application webhook data purportedly "from" a shop that the request was never actually authenticated for. If a host app uses `data.shop` (as the docs instruct) to key merchant-scoped storage, trigger merchant-scoped side effects, or fetch/update per-shop state without re-verifying shop association some other way, the attacker can inject fabricated events attributed to an arbitrary victim shop — a cross-tenant data/state injection through the gem's own documented `process`/`WebhookMetadata` contract, not a host-app misuse.

### Likelihood Explanation
Requires only an unprivileged attacker who can install the target app on their own (attacker-controlled) shop — a normal, unprivileged action available to anyone — and the ability to send an HTTP request to the app's public webhook endpoint with a modified header. No access to `api_secret_key`, no TLS interception, and no privileged account is needed.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the signed material verified against the HMAC, or independently validate that `request.shop` corresponds to a shop with an active, previously-established session/installation known to the app before handing it to the handler as trusted tenant context.

### Proof of Concept
```ruby
# 1. Attacker installs the app on their own shop "attacker.myshopify.com"
#    and receives a legitimate webhook for it:
raw_body = '{"id": 1, "note": "legit payload from attacker'\''s own shop"}'
valid_hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), api_secret_key, raw_body)
# Shopify sends this hmac in "x-shopify-hmac-sha256" (base64) with
# "x-shopify-shop-domain: attacker.myshopify.com"

# 2. Attacker replays the same body/hmac but swaps the shop-domain header:
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(valid_hmac), # unchanged, still valid for raw_body
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # attacker-controlled, unauthenticated
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) passes (only raw_body is checked)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: ..., ...))
# The host app now processes attacker-controlled data under "victim-shop.myshopify.com"'s identity.
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

**File:** docs/usage/webhooks.md (L10-27)
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
```
