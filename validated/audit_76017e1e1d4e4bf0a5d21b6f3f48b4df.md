### Title
Webhook `shop` identity is not bound to the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook’s `shop` field as an authenticated tenant identifier once `Utils::HmacValidator.validate` succeeds, but the HMAC only ever covers the raw request body, never the `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header. This breaks the binding `HMAC-verified bytes == bytes used to identify the tenant`, letting an attacker replay a legitimate (body, hmac) pair while attaching an arbitrary victim shop domain, causing the app to process attacker-controlled webhook data under the victim's identity.

### Finding Description
`ShopifyAPI::Webhooks::Request` extracts the shop from an unauthenticated header: [1](#0-0) 

Its HMAC signable content is defined as only the raw body: [2](#0-1) 

`HmacValidator.validate` computes/compares the signature strictly against `to_signable_string`, i.e. the body only, with no reference to `shop`, `topic`, or `webhook_id`: [3](#0-2) 

`Registry.process` runs the HMAC check and then unconditionally forwards `request.shop` (the unauthenticated header) to the app’s handler as the trusted tenant identifier: [4](#0-3) 

The library's own documentation instructs integrators to treat `data.shop` as the authoritative shop for the webhook and use it directly for tenant-scoped routing/storage (e.g. `shop_domain: data.shop`), which is exactly how `Registry.process` is designed to be used: [5](#0-4) 

Because the shop header sits entirely outside the cryptographic envelope, any attacker who can obtain one legitimate `(raw_body, hmac)` pair for the app's secret — trivially available to anyone who installs the app on their own shop and receives a genuine webhook — can replay that exact body and HMAC to the app's public webhook endpoint while substituting a different `X-Shopify-Shop-Domain` value. `HmacValidator.validate` still returns `true` (it only checks the body), and the handler is invoked believing the body belongs to the victim shop.

### Impact Explanation
This is a cross-tenant confusion/injection primitive supplied directly by the gem: the library asserts the request is "verified" (`InvalidWebhookError` is only raised on body-HMAC mismatch) and then hands the caller a `shop` value that carries no cryptographic assurance. Any application built on the documented `WebhookMetadata`/`Registry.process` contract inherits the flaw without doing anything wrong, since it is following the gem's documented API exactly. Depending on the webhook topic, this can let an attacker inject fabricated resource-lifecycle events (e.g. `orders/create`, `app/uninstalled`, `shop/redact`) attributed to a shop they do not control, corrupting or exfiltrating data associated with another tenant.

### Likelihood Explanation
Exploitation requires only: (1) the attacker's own legitimate `(body, hmac)` pair, obtainable for free by installing the target app on an attacker-owned development store, and (2) the ability to POST to the app's public webhook endpoint with a forged `shop-domain`/`x-shopify-shop-domain` header — no secrets, tokens, or privileged access are required. This is a low-effort, no-credential attack path fully rooted in this gem's verification logic.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the value that is HMAC-verified (or otherwise cryptographically bind them, e.g. via a signed envelope or independently confirming shop identity via a Shopify API call before trusting it), rather than only signing the raw body. At minimum, `Webhooks::Registry.process` should not treat `request.shop` as authenticated identity for tenant-scoped operations unless it is covered by the same signature that gates `InvalidWebhookError`.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives a genuine webhook (e.g. `orders/create`), capturing the raw body `B` and its valid header `X-Shopify-Hmac-Sha256: H` (computed by Shopify over `B` with the app's secret).
2. Attacker resends this exact request to the app's public webhook endpoint, keeping body `B` and header `H` unchanged, but replacing:
   `X-Shopify-Shop-Domain: attacker.myshopify.com` → `X-Shopify-Shop-Domain: victim.myshopify.com`
3. `ShopifyAPI::Webhooks::Request.new` parses the forged shop header; `Utils::HmacValidator.validate` recomputes HMAC over `B` only and it matches `H`, so `Registry.process` does not raise `InvalidWebhookError`.
4. `Registry.process` invokes the app's handler with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: JSON.parse(B), ...)`, so the app processes attacker-controlled data as if it originated from the victim shop.

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

**File:** docs/usage/webhooks.md (L10-29)
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
