### Title
`Webhooks::Request#topic`/`#shop`/`#api_version` are unauthenticated headers not covered by the webhook HMAC, letting an attacker replay their own validly-signed body under a forged topic and shop - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , so `Utils::HmacValidator.validate` only proves the body was signed with `api_secret_key`, never that the `topic`, `shop`, or `api_version` headers were the ones Shopify actually sent alongside that body [2](#0-1) . `Registry.process` then dispatches solely on `request.topic` and passes `request.shop` unchecked into `WebhookMetadata` [3](#0-2) .

### Finding Description
The claimed binding is: `hmac == HMAC(secret, raw_body)` should imply `(raw_body, topic, shop, api_version)` as a unit was produced by Shopify for that shop/topic. In the code this binding does not hold — `hmac` covers `raw_body` only:

```
lib/shopify_api/webhooks/request.rb:35-38
def to_signable_string
  @raw_body
end
```

`topic`, `shop`, and `api_version` are read straight from attacker-controllable headers (`shopify_header`), with no cryptographic tie to `hmac` [4](#0-3) . `HmacValidator.validate` recomputes `HMAC(secret, to_signable_string)` and secure-compares it to the received `hmac`, never touching topic/shop [5](#0-4) . `Registry.process` accepts any `Request` that passes this check and looks up the handler purely by `request.topic`, then forwards `request.shop` unchanged into `WebhookMetadata` [3](#0-2) .

Because `api_secret_key` is shared across every shop that installs the same app, an attacker who installs the app on their own development shop can legitimately receive one authentic `(raw_body, hmac)` pair for any topic they subscribe to. They can then POST that exact `raw_body` and `X-Shopify-Hmac-Sha256` value directly to the app's public webhook callback URL, while freely setting `X-Shopify-Topic` and `X-Shopify-Shop-Domain` to any values they want (e.g. `app/uninstalled` and a victim shop's domain). `HmacValidator.validate` still returns `true` because the body/HMAC pair is genuinely valid for that secret; `Registry.process` then invokes whatever handler is registered for the forged topic, with `WebhookMetadata#shop` set to the forged victim domain [6](#0-5) .

No other check in this gem re-derives or constrains `topic`/`shop` from the signature — `ShopValidator`, `JwtPayload`, and `Context` guards apply to OAuth/session-token flows, not to `Webhooks::Request`, and nothing in `request.rb` or `registry.rb` cross-checks these header values against the signed content.

### Impact Explanation
An attacker who can install the target app on any shop (including their own free dev store) can produce a valid `(raw_body, hmac)` pair once, then replay it against the app's public webhook endpoint with an arbitrary forged `topic` and `shop` header. If the host app's handler trusts `WebhookMetadata#shop`/`#topic` for authorization or data-scoping decisions (e.g. `app/uninstalled` cleanup, GDPR `customers/redact`, or any handler keyed by topic to decide what mutation to run on `shop`), the attacker can trigger that handler's logic against an arbitrary victim shop identifier with attacker-chosen body content. This is a cross-tenant impact: one tenant's signed traffic is used to manipulate state associated with a different tenant's identifier, matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Preconditions are low-cost and fully within the stated attacker capability: the attacker needs only to (1) create a development shop, (2) install the target app to receive one legitimately signed webhook for any topic, (3) know or guess the app's public webhook receiver URL (typically documented or discoverable), and (4) send a forged POST with the captured body/HMAC and altered `X-Shopify-Topic`/`X-Shopify-Shop-Domain` headers. No secret key, session, or access token is required, and the attack is repeatable indefinitely against any shop domain the attacker chooses to put in the header, without ever needing a genuine webhook for that shop.

### Recommendation
Bind `topic`, `shop`, and `api_version` into the signable string (or otherwise authenticate them), e.g. change `to_signable_string` to include the header values alongside `raw_body`, and require the host app to pass the expected/registered topic and shop to `Registry.process` for cross-checking, rather than trusting header values sourced independently of the HMAC.

### Proof of Concept
minitest (WebMock/Mocha) plan under `test/webhooks/`:
1. Configure `Context` with a known `api_secret_key`.
2. Build `raw_body = '{"id":1}'`, compute `hmac = HMAC-SHA256(secret, raw_body)` (base64), and construct `Request.new(raw_body: raw_body, headers: {"x-shopify-topic" => "orders/create", "x-shopify-hmac-sha256" => hmac, "x-shopify-shop-domain" => "attacker.myshopify.com"})`. Assert `Utils::HmacValidator.validate(request)` is `true`.
3. Construct a second `Request.new` with the identical `raw_body` and `hmac`, but `headers: {"x-shopify-topic" => "app/uninstalled", "x-shopify-hmac-sha256" => hmac, "x-shopify-shop-domain" => "victim.myshopify.com"}`. Assert `Utils::HmacValidator.validate(request)` is also `true`.
4. Assert `request_1.topic != request_2.topic` and `request_1.shop != request_2.shop` while both pass the same HMAC check, demonstrating that `hmac` binds only `raw_body`, not `topic`/`shop`.
5. Optionally call `Registry.process(request_2)` with a stubbed `app/uninstalled` handler registered, and assert the handler is invoked with `WebhookMetadata#shop == "victim.myshopify.com"` despite the signed payload never having been produced for that shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-28)
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

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
