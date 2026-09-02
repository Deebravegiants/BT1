### Title
Webhook `shop` attribute is read from an unsigned header while `HmacValidator` only covers the raw body, enabling cross-tenant webhook replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`Webhooks::Request#to_signable_string` returns only `@raw_body`, and `Webhooks::Request#shop` is read from the unsigned `shopify-shop-domain`/`x-shopify-shop-domain` header. `Utils::HmacValidator.validate` verifies only the signable string (the body), so the HMAC check never binds the claimed `shop` to the signature, letting an attacker who owns a valid (body, hmac) pair from their own shop relabel it as coming from any other shop.

### Finding Description
The broken binding is: `request.shop` (used by `Registry.process` to build `WebhookMetadata.shop`, which is handed to the host app's `WebhookHandler#handle`) should equal the shop that produced the HMAC-signed `raw_body`, but it does not, because `shop` is derived from a header that is excluded from `to_signable_string`.

- `Request#to_signable_string` returns `@raw_body` only: [1](#0-0) 
- `Request#shop` reads the unsigned header: [2](#0-1) 
- `HmacValidator.validate_signature` computes the signature strictly over `verifiable_query.to_signable_string`, i.e., the body, and never touches `shop`: [3](#0-2) 
- `Registry.process` gates only on `HmacValidator.validate(request)` and then forwards `request.shop` straight into `WebhookMetadata`, which is passed to the host app's handler as the tenant identity: [4](#0-3) [5](#0-4) 

Exploit flow: an attacker installs the target app on their own shop and receives a legitimately Shopify-signed webhook (`raw_body`, `x-shopify-hmac-sha256`) addressed to their own shop. They then send an HTTP request to the app's webhook endpoint with the identical `raw_body` and `x-shopify-hmac-sha256`, but with `x-shopify-shop-domain` (or `shopify-shop-domain`) rewritten to a victim shop's domain. `HmacValidator.validate` recomputes the HMAC over `raw_body` only, using the app's `Context.api_secret_key`; since the body is unmodified and the secret is the same app's secret, the signature matches. `request.shop` then evaluates to the attacker-chosen victim domain, and `Registry.process` dispatches `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...)` to the handler, which will act on attacker-controlled body content under the victim's tenant identity. No existing guard intercepts this: `HmacValidator.validate` (body-only check) passes, there is no `ShopValidator.sanitize!`/known-shop check anywhere in `Registry.process`, and Sorbet typing only enforces that `shop` is a `String`, not that it corresponds to the signed payload.

### Impact Explanation
This lets an unprivileged attacker with only their own dev shop and app installation forge the shop attribution of a webhook payload processed by the host app, causing the host app to write/act on data (e.g., order, product, or GDPR-topic payloads) as if it belonged to an arbitrary victim shop. This is a cross-tenant data integrity/access violation: whichever data a host app keys off `WebhookMetadata#shop` (e.g., updating that shop's local records, triggering per-shop side effects) can be poisoned or misattributed by a completely different, uninvolved shop. It is repeatable indefinitely and against any victim shop string the attacker chooses, since the exploit only depends on the attacker's own valid (body, hmac) pair and knowledge of the endpoint URL, matching the Critical "cross-tenant access" category.

### Likelihood Explanation
Preconditions are low-cost and match the documented attacker model: create/own a development shop, install the target app, receive one legitimate webhook callback, and replay it to the app's public webhook endpoint with a modified `shop-domain` header. No secrets, tokens, or privileged access are required. Because the webhook endpoint path is typically shared across all shops installing the same app (only `shop-domain` distinguishes tenants), this is trivially repeatable for any topic the app subscribes to and for any victim shop domain the attacker chooses to type into the header.

### Recommendation
Bind `shop` into the signature verification, or otherwise cross-check it against a known, previously-authenticated identity before trusting it. Concretely: (1) do not allow the header-provided `shop` to be treated as authoritative tenant identity for downstream processing without confirming it corresponds to a shop that legitimately has this app installed (e.g., look up an existing session/access token for that shop and treat unknown shops as invalid), and/or (2) document/enforce that host apps must independently validate `WebhookMetadata#shop` against their own installed-shops registry before using it, since the HMAC in this gem (matching Shopify's webhook signing scheme) never covers the shop domain.

### Proof of Concept
```ruby
# test/webhooks/request_test.rb (new test)
def test_shop_can_be_spoofed_despite_valid_hmac
  raw_body = "{}"
  hmac = OpenSSL::HMAC.digest(
    OpenSSL::Digest.new("sha256"),
    ShopifyAPI::Context.api_secret_key,
    raw_body,
  )
  headers = {
    "x-shopify-topic" => "orders/create",
    "x-shopify-hmac-sha256" => Base64.encode64(hmac), # genuinely valid for raw_body
    "x-shopify-shop-domain" => "victim-shop.myshopify.com", # attacker-chosen, unsigned
  }

  request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)

  assert(ShopifyAPI::Utils::HmacValidator.validate(request)) # signature check passes
  assert_equal("victim-shop.myshopify.com", request.shop)    # yet shop is attacker-controlled
end
```
This demonstrates both sides of the claimed equality diverging: the HMAC validates successfully (left side: `HmacValidator.validate(request) == true`), while `request.shop` (right side, used downstream by `Registry.process`/`WebhookMetadata`) equals an attacker-chosen victim domain rather than the shop that actually produced the signed body.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
