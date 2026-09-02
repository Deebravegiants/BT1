### Title
Webhook `shop` attribution is not covered by the HMAC signature, allowing cross-tenant shop spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` reads the `shop` domain from the unauthenticated `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, while the HMAC signature validated by `Utils::HmacValidator` only covers the raw request body. This breaks the identity binding "shop authenticated == shop the data is attributed to."

### Finding Description
`Request#shop` is derived purely from a header value: [1](#0-0) 

The HMAC that `Registry.process` validates is computed only over `to_signable_string`, which returns `@raw_body` and nothing else — it does not include `shop`, `topic`, `webhook_id`, or any other header: [2](#0-1) 

`HmacValidator.validate` computes and compares the signature strictly against `to_signable_string`: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately forwards `request.shop` (the unauthenticated header value) to the host application's handler as the shop of record: [4](#0-3) 

The gem's own documentation instructs host apps to treat `data.shop` as the authoritative shop identifier for the webhook payload (e.g., to key database writes, job dispatch, etc.): [5](#0-4) 

Because the shop header is excluded from the signed bytes, the equality the gem is supposed to guarantee — `shop authenticated by HMAC == shop attributed to the payload` — does not hold. Any party capable of relaying a validly-HMAC-signed body to the app's webhook endpoint (e.g., a merchant on their own installed shop who receives genuine signed webhooks for their own shop and can freely alter and replay the outer HTTP request before it reaches the app) can substitute an arbitrary `shopify-shop-domain` header value. The HMAC check still passes because it is computed only over the body, and `Registry.process` will hand off the body content labeled with a shop domain of the attacker's choosing to the handler.

### Impact Explanation
This lets an unprivileged actor cause a webhook body to be misattributed to a different, victim tenant (`shop`), because the gem's own verification step never binds the shop identity to the signed content. Host applications that follow the documented pattern of trusting `data.shop` for tenant-scoped operations (data storage, job routing, redact/GDPR requests, etc.) can have data cross tenant boundaries — a cross-tenant access condition rooted entirely in this gem's `VerifiableQuery`/`HmacValidator` design (`to_signable_string` omitting `shop`), not a documented app-side ignoring of the gem's contract, since the gem itself hands the caller a `shop` field advertised as validated context.

### Likelihood Explanation
Requires no possession of `api_secret_key`, no privileged account, and no TLS interception: an attacker only needs the ability to send an HTTP POST to the app's public webhook endpoint with a replayed/self-obtained valid body+HMAC pair (available to them from webhooks Shopify already sent to their own shop) and an arbitrary `shopify-shop-domain` header. The signature check has no dependency on that header, so likelihood of successful exploitation is high once the endpoint is reachable.

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`) in the signable content that `Webhooks::Request#to_signable_string` returns and verify it against the value read by `Request#shop`, or otherwise cryptographically bind the header-derived shop domain to the HMAC-covered payload before it is exposed via `WebhookMetadata`.

### Proof of Concept
1. App merchant "Shop A" installs the app; Shopify sends a legitimate webhook to the app's callback URL: body `B`, header `shopify-hmac-sha256: HMAC(secret, B)`, header `shopify-shop-domain: shop-a.myshopify.com`.
2. The attacker (operator of Shop A, an unprivileged actor with respect to other tenants) intercepts/replays this exact request to the app's webhook endpoint but rewrites the header to `shopify-shop-domain: victim-shop.myshopify.com`, leaving body `B` and the HMAC header untouched.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC only over `request.to_signable_string` (i.e., `B`) and finds it valid [2](#0-1) .
4. `Registry.process` builds `WebhookMetadata` with `shop: request.shop`, which now returns `"victim-shop.myshopify.com"` [6](#0-5) .
5. The host application's handler receives body `B` attributed to `victim-shop.myshopify.com`, per the documented `data.shop` contract [7](#0-6) , resulting in cross-tenant data misattribution.

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

**File:** docs/usage/webhooks.md (L12-29)
```markdown
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
