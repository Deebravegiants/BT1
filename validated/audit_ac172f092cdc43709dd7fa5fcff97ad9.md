### Title
Webhook `shop` attribution trusts unsigned `X-Shopify-Shop-Domain` header, allowing cross-tenant payload attribution - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`Request#shop` reads the shop domain directly from the `x-shopify-shop-domain`/`shopify-shop-domain` header, which is not covered by the HMAC signature computed over `@raw_body`. Because Shopify webhook HMACs are computed with the app's single shared `api_secret_key` (not a per-shop secret), any shop that legitimately installs the app can capture a validly-signed webhook payload delivered to its own endpoint and replay that exact body+HMAC to the shared app endpoint with the shop-domain header rewritten to an arbitrary victim shop, causing the app to process the attacker's payload as if it belongs to the victim.

### Finding Description
The binding that should hold is: **shop authenticated by the HMAC over `@raw_body`** must equal **the shop the app attributes the event to via `request.shop`**. Tracing the code:

- `Request#shop` simply returns the raw header value with no cryptographic binding: [1](#0-0) 
- `Request#to_signable_string` (what `HmacValidator` actually signs/verifies) is only `@raw_body` — headers, including `shop-domain`, are excluded entirely: [2](#0-1) 
- `HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` (the body) and compares it to `verifiable_query.hmac`; it never inspects or validates `shop`: [3](#0-2) 
- `Registry.process` validates the HMAC, then immediately trusts `request.shop` to build `WebhookMetadata` and dispatch to the handler — the only gate is the body's HMAC, not the shop attribution: [4](#0-3) 

Because the HMAC secret (`Context.api_secret_key`) is shared across all shops that install the app (it is the app's client secret, not a per-shop secret), any attacker who installs the app on their own development shop and receives one legitimately-signed webhook has a body+HMAC pair that will pass `HmacValidator.validate` regardless of which shop-domain header accompanies it. The attacker then POSTs that same body and HMAC to the app's shared webhook endpoint with `X-Shopify-Shop-Domain` rewritten to an arbitrary victim shop's domain. `Request.new` accepts the forged header (it only checks for header *presence*, not authenticity), `HmacValidator.validate` returns true (it only checks the body signature), and `Registry.process` calls `handler.handle` with `WebhookMetadata#shop` set to the victim's domain while the body content is entirely the attacker's own shop's data.

None of the existing guards catch this: `HmacValidator.validate` only binds the body, `ShopValidator`/`state`/JWT checks are unrelated to this webhook path, and Sorbet typing only enforces that `shop` is a `String`, not that it is authentic.

### Impact Explanation
The app's webhook handler receives the attacker's own event body while believing it belongs to an arbitrary victim shop chosen by the attacker. Any app logic keyed off `request.shop`/`WebhookMetadata#shop` (e.g., looking up the victim's session/access token to act on their store, writing the attacker's data into the victim's tenant record, or triggering mandatory-topic side effects like `shop/redact` against the wrong shop) is corrupted. This is a cross-tenant data injection primitive — Critical per the rubric's "cross-tenant access" category. It is repeatable against any shop, and requires no secrets beyond what any shop owner installing the app already has (their own valid webhook deliveries).

### Likelihood Explanation
Preconditions are minimal and fully within the attacker's control per the threat model: create a development shop, install the target app, receive at least one legitimate webhook (any topic works, since only the body/HMAC pair need to be replayed), then send a single forged HTTP request to the app's public webhook endpoint with a rewritten `X-Shopify-Shop-Domain` header. No credentials, secrets, or victim cooperation are required, and it works against arbitrary victim shop domains chosen by the attacker (shop domains are guessable/enumerable as `*.myshopify.com`). This is highly feasible and repeatable.

### Recommendation
Do not treat `Request#shop` as authenticated tenant identity. Either (a) include the shop domain in the signed payload verification path (Shopify's webhook body already contains shop-scoped data, but the gem should not expose an unauthenticated `shop` accessor as if it were trustworthy), or (b) require callers to cross-check `request.shop` against the shop associated with the session/access token used to register that specific webhook subscription (e.g., verify the topic+shop combination against Shopify's webhook subscription records) before acting on the payload. At minimum, document prominently that `request.shop` is unauthenticated and must not be used as the sole tenant-dispatch key.

### Proof of Concept
```ruby
# test/webhooks/request_shop_spoof_test.rb
require_relative "../test_helper"

class RequestShopSpoofTest < Minitest::Test
  def setup
    ShopifyAPI::Context.setup(api_key: "key", api_secret_key: "secret", ...)
  end

  def test_hmac_validation_ignores_shop_domain_header
    body = '{"id":1,"note":"attacker shop A data"}'
    valid_hmac = Base64.strict_encode64(
      OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), "secret", body)
    )

    # Attacker's own legitimately-signed webhook, shop A
    honest_request = ShopifyAPI::Webhooks::Request.new(
      raw_body: body,
      headers: {
        "x-shopify-topic" => "orders/create",
        "x-shopify-hmac-sha256" => valid_hmac,
        "x-shopify-shop-domain" => "attacker-shop-a.myshopify.com",
      },
    )
    assert ShopifyAPI::Utils::HmacValidator.validate(honest_request)
    assert_equal "attacker-shop-a.myshopify.com", honest_request.shop

    # Same body+hmac, replayed with victim's shop header
    forged_request = ShopifyAPI::Webhooks::Request.new(
      raw_body: body,
      headers: {
        "x-shopify-topic" => "orders/create",
        "x-shopify-hmac-sha256" => valid_hmac,
        "x-shopify-shop-domain" => "victim-shop-b.myshopify.com",
      },
    )

    # HMAC still validates -- proves shop is outside signature coverage
    assert ShopifyAPI::Utils::HmacValidator.validate(forged_request)
    # But shop attribution is now attacker-controlled/incorrect
    assert_equal "victim-shop-b.myshopify.com", forged_request.shop
    assert_equal honest_request.parsed_body, forged_request.parsed_body

    # Binding violated: HMAC-authenticated shop (A) != attributed shop (B)
    refute_equal honest_request.shop, forged_request.shop
  end
end
```
This demonstrates that `HmacValidator.validate` passing says nothing about `request.shop` correctness, and that `Registry.process` (which calls both) will dispatch the attacker's body under the victim's identity.

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
