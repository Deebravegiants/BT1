### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing shop-identity spoofing in a valid webhook request - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, then trusts a separate, unsigned HTTP header (`x-shopify-shop-domain` / `shopify-shop-domain`) to identify which tenant the event belongs to. The `shop` value is never included in the HMAC-signed material, so it is possible to present a validly-signed webhook body under an attacker-chosen shop identity.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`shop` is read from a plain header, never mixed into the HMAC input: [2](#0-1) 

`Registry.process` validates only the body's HMAC, then forwards `request.shop` (the unauthenticated header) straight to the app's handler as the tenant identifier: [3](#0-2) 

`HmacValidator.validate` confirms the signature is computed only from `verifiable_query.to_signable_string` (body only) against the shared `api_secret_key`: [4](#0-3) 

The documented contract explicitly tells host apps to trust `data.shop` as "The shop domain of the webhook" and use it for per-tenant dispatch (e.g. `shop_domain: data.shop`): [5](#0-4) 

The binding that should hold is: `shop header used for tenant routing == shop bound by the cryptographic signature`. Because the HMAC only covers the body, this equality does not hold — the header can be modified independently of the signature without invalidating it, since `OpenSSL.secure_compare(computed_signature, received_signature)` only checks the body bytes, not the header bytes.

### Impact Explanation
An attacker who can obtain one genuinely Shopify-signed webhook body (webhook bodies are not always confidential — e.g., `app/uninstalled`, `shop/update`, or other low-sensitivity topics, or bodies leaked via logs, error trackers, browser devtools in a merchant's own shop, etc.) can replay that exact body to the app's single shared webhook endpoint while substituting the `x-shopify-shop-domain` header for a different, victim shop. Since the HMAC check only re-validates the body against the shared `api_secret_key` (the same secret for all shops of the app), the signature still validates. The host application then processes the event under the attacker-chosen `shop`, which can pollute or corrupt data belonging to a different tenant — a cross-tenant integrity/confusion issue. This satisfies the "cross-tenant access" criterion for a Critical/High rated finding, given the gem's documented API explicitly instructs apps to key off `data.shop` for shop-scoped work.

### Likelihood Explanation
Exploitation requires only capture/knowledge of one legitimately-signed webhook body for the app (secret material is not required — only a previously delivered body, which the requester's own shop can generate freely by triggering any subscribed webhook topic on their own store) and the ability to POST to the app's public webhook endpoint with a spoofed header, which is fully controllable by any unprivileged internet client. No access token, `api_secret_key`, or privileged account is needed.

### Recommendation
Bind the shop identity cryptographically to the signature rather than relying on an out-of-band header:
- Include the `x-shopify-shop-domain` value in the string that is HMAC-signed/verified in `Request#to_signable_string`, or
- Have `Registry.process` cross-check `request.shop` against an authoritative source (e.g., look up the specific per-shop webhook secret / registered shop for the given `webhook_id`) rather than trusting the header verbatim, and
- Document clearly that `data.shop` in `WebhookMetadata` is only as trustworthy as the header, requiring host apps to independently validate shop ownership when performing shop-scoped writes.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and subscribes to a webhook topic (e.g. `app/uninstalled`), receiving a legitimately Shopify-signed POST to the app's public webhook endpoint:
   - Headers: `x-shopify-hmac-sha256: <valid-hmac-of-body>`, `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-topic: app/uninstalled`
   - Body: `{}` (or any signed payload from `attacker.myshopify.com`)
2. Attacker replays the exact same body and HMAC header to the same endpoint, but changes only the `x-shopify-shop-domain` header to `victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the modified headers; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC only over `@raw_body` — unchanged — so validation succeeds: [6](#0-5) 
4. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` even though the payload actually originated from and describes `attacker.myshopify.com`, causing the host app to act on the wrong tenant's behalf.

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

**File:** docs/usage/webhooks.md (L12-30)
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
```
