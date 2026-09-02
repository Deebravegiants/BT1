This confirms the vulnerability pattern. The gem's own documentation explicitly instructs apps to trust `data.shop` from the webhook payload as the tenant identifier for downstream processing, while the HMAC signature in `ShopifyAPI::Webhooks::Registry.process` only covers the raw JSON body, not the `shop-domain`/`topic`/`webhook-id` headers.

### Title
Webhook tenant identity (`shop-domain` header) is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body [1](#0-0) . The `shop`, `topic`, and `webhook_id` values that the gem hands to the app's handler as the trusted tenant/routing identity come from HTTP headers that are never included in the signed payload [2](#0-1) .

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [3](#0-2) , and `Utils::HmacValidator.validate` computes/compares the HMAC exclusively against that signable string [4](#0-3) . Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from HTTP headers (`shopify-shop-domain`, `shopify-topic`, etc.) with no cryptographic binding to the body or to each other [5](#0-4) . `Registry.process` validates only `Utils::HmacValidator.validate(request)` and then forwards `request.shop` unchanged into `WebhookMetadata` passed to the app's handler [1](#0-0) .

The identity binding broken is: **HMAC-verified bytes (body only) ≠ bytes the app trusts as tenant identity (`shop` header)**. The gem's own documentation instructs integrators to treat `data.shop` as the authoritative shop for that webhook and to key downstream processing (e.g., background jobs) by it [6](#0-5) , so this header is the de facto tenant identifier despite carrying no signature coverage.

### Impact Explanation
Because the app's `client_secret` is shared across all shops that install the app, any unprivileged user who legitimately installs the app on their own shop can capture a genuinely-signed `(raw_body, hmac)` pair from a webhook Shopify sends them, then replay that exact body/HMAC to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`/`Webhook-Id`) header for a different, victim shop that also uses the app. `Utils::HmacValidator.validate` still succeeds (same secret, same body bytes) [7](#0-6) , and `Registry.process` dispatches the attacker's body to the handler tagged with the victim's `shop` [8](#0-7) . This is a cross-tenant confusion: the app processes attacker-controlled data as if it originated from the victim tenant, which can corrupt the victim's records, trigger unwanted actions scoped to the victim's session/store, or leak the attacker's own data into the victim's context depending on how the host app uses `data.shop`/`data.body`.

### Likelihood Explanation
Requires only that the attacker be an app user (any merchant installing a public app) capable of sending arbitrary HTTP POST requests to the app's public webhook endpoint — no privileged credentials, TLS interception, or leaked secrets needed. The webhook endpoint is by design unauthenticated aside from the HMAC, and the attack only needs one legitimately-received webhook (which any installer receives automatically) to obtain a valid `(body, hmac)` pair.

### Recommendation
Include the tenant-identifying fields (`shop`, `topic`, `webhook_id`, `api_version`) in the value that is HMAC-verified, or otherwise cryptographically bind them to the body (e.g., verify a signature over the concatenation of headers + body, or require the app to independently confirm that the `shop` header corresponds to a shop with a currently-registered webhook subscription matching `webhook_id` before trusting it). At minimum, document prominently that `data.shop`/`data.topic` are unauthenticated and must not be used as sole tenant-routing keys without additional server-side verification (e.g., cross-checking against the app's own webhook subscription records by `webhook_id`).

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and subscribes to `orders/create`.
2. Shopify sends a legitimate webhook to the app's endpoint:
   - Headers: `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Topic: orders/create`, `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>`
   - Body: `{"id": 1, "note": "hello"}`
3. Attacker captures this exact `raw_body` and `X-Shopify-Hmac-Sha256` value.
4. Attacker replays the identical body/HMAC to the same endpoint but changes `X-Shopify-Shop-Domain` to `victim.myshopify.com` (a real installer of the same app).
5. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Utils::HmacValidator.validate` succeeds because it only checks `@raw_body` against the HMAC [3](#0-2) .
6. `Registry.process` calls the app's handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: {"id"=>1,"note"=>"hello"}, ...)` [9](#0-8) , causing the host app to process attacker-supplied data under the victim shop's tenant context.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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
