### Title
Webhook `shop-domain` (and `topic`/`webhook_id`/`api_version`) headers are trusted by `Registry.process` without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, and `Utils::HmacValidator.validate` verifies the HMAC exclusively against that raw body. The `shop-domain`, `topic`, `webhook-id`, and `api-version` values are read straight from HTTP headers and are never included in the signed material, yet `Registry.process` forwards `request.shop`, `request.topic`, and `request.webhook_id` unchecked into the handler's `WebhookMetadata`.

### Finding Description
`Utils::HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it against the `hmac` field [1](#0-0) . For webhooks, `to_signable_string` is simply `@raw_body` [2](#0-1) . Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all pulled from headers with no cryptographic binding to the signature [3](#0-2) .

`Registry.process` validates only the HMAC over the body and then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` to build `WebhookMetadata` passed to the app's handler: [4](#0-3) .

The equality this breaks: **shop authenticated (bytes covered by HMAC = raw body only) ≠ shop acted on (the `x-shopify-shop-domain` header value used by the app to attribute the event)**.

### Impact Explanation
Because the header carrying the shop identity is not part of the signed payload, a request with a *valid* HMAC (any body+signature pair a merchant/attacker legitimately received from Shopify for their own store, or any raw body they can otherwise get validly signed) can be replayed to the app's webhook endpoint with an arbitrary `x-shopify-shop-domain` header. `Registry.process` will still pass HMAC validation (it only checks the body) and will dispatch the handler believing the event belongs to a different shop. Depending on how the host app uses `data.shop` (e.g., to look up shop-specific settings, apply the payload to that tenant's records, or trigger shop-specific side effects), this enables cross-tenant data confusion — an unprivileged actor who is a legitimate merchant with the app installed (no `api_secret_key`, no access token, no privileged account needed) can attribute genuine webhook bodies to a victim shop of their choosing.

### Likelihood Explanation
Exploitation requires the attacker to control a merchant store where the app is installed (to receive genuinely-signed webhook bodies for arbitrary content they can influence, e.g. via `products/update`) and to be able to POST directly to the app's public webhook endpoint with custom headers — both realistic for any external actor without special credentials. The gem's own test suite demonstrates the header/body split explicitly (HMAC is computed purely over `"{}"`while `x-shopify-shop-domain` is set independently) [5](#0-4) , confirming this is the intended verification design of the gem, not a use error by the host app.

### Recommendation
Document (and/or enforce) that `data.shop` from `Registry.process` must never be trusted as an authenticated tenant identifier on its own — apps must correlate the shop domain against a shop known to have registered that specific `webhook_id`/topic via their session store, or Shopify should be asked to include the shop domain in the signed payload. At minimum, update `docs/usage/webhooks.md` to explicitly warn that only the body is HMAC-verified and that header-derived fields (`shop`, `topic`, `webhook_id`, `api_version`) are unauthenticated and must be cross-checked against the app's own persisted shop/session records before being used for any tenant-scoped action.

### Proof of Concept
1. App has `WebhookHandler#handle` implemented per the documented pattern, using `data.shop` to look up/act on shop-specific state [6](#0-5) .
2. Attacker installs the app on their own store `attacker.myshopify.com` and receives a legitimate webhook POST from Shopify (valid body + valid `x-shopify-hmac-sha256`).
3. Attacker replays that exact body and HMAC header to the app's public webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `raw_body` against the (unchanged) signature [7](#0-6) .
5. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and the attacker-influenced body, and performs whatever shop-scoped action the app implements for that webhook — cross-tenant impact without needing the victim's or the app's credentials.

**Note on confidence:** I was not able to verify from this gem alone whether Shopify's real-world webhook delivery would ever let an unprivileged party obtain a validly-signed body they can freely craft content for (this depends on which topics/fields end up in the body and how permissive the app's handler logic is), so real-world exploitability partly depends on the host application's handler logic, which is outside this gem's index. This is flagged as uncertain and would benefit from further confirmation in a full Devin session with access to real webhook payload examples and a candidate host app's handler implementation.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
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

**File:** test/webhooks/registry_test.rb (L16-28)
```ruby
        hmac = OpenSSL::HMAC.digest(
          OpenSSL::Digest.new("sha256"),
          ShopifyAPI::Context.api_secret_key,
          "{}",
        )

        @headers = {
          "x-shopify-topic" => @topic,
          "x-shopify-hmac-sha256" => Base64.encode64(hmac),
          "x-shopify-shop-domain" => @shop,
          "x-shopify-webhook-id" => "b1234-eefd-4c9e-9520-049845a02082",
          "x-shopify-api-version" => "2024-01",
        }
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
