### Title
Webhook `shop` domain is not part of the HMAC-signed bytes, allowing a valid signature from one shop to be replayed under a forged tenant identity - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so `Utils::HmacValidator.validate_signature` verifies solely that the body bytes were signed with `Context.api_secret_key`; it never checks that the `x-shopify-shop-domain` header corresponds to the shop that legitimately produced that body/HMAC pair. `Registry.process` then trusts `request.shop` (read straight off that unauthenticated header) to build `WebhookMetadata` and dispatches it to the handler as the tenant identity.

### Finding Description
The binding the finding claims should hold is: `shop authenticated by HMAC == shop acted on by handler`, i.e. `hmac_signer(raw_body, secret) → shop_S` should equal `request.shop → shop_S`. Tracing the code:

- `Request#to_signable_string` returns `@raw_body` only, `x-shopify-shop-domain` is never included in the bytes that get HMAC'd: [1](#0-0) 
- `Request#shop` simply reads the `x-shopify-shop-domain`/`shopify-shop-domain` header verbatim, with no cross-check against the signed content: [2](#0-1) 
- `HmacValidator.validate_signature` computes the HMAC over `verifiable_query.to_signable_string` (i.e. body only) and compares it against the received `hmac` header with `OpenSSL.secure_compare`: [3](#0-2) 
- `Registry.process` only calls `Utils::HmacValidator.validate(request)` (body/secret check) and, once that passes, builds `WebhookMetadata` using `request.shop` — the same unauthenticated header — and dispatches to the handler: [4](#0-3) 

Because `Context.api_secret_key` is one shared value for the whole app (not per-installation), a body+HMAC pair that Shopify genuinely produced for the attacker's own dev-shop webhook remains a valid `(body, hmac)` pair under that same secret regardless of which shop domain is attached to the request. An attacker can install the app on a shop they control, capture a real webhook delivery (raw body + `x-shopify-hmac-sha256`), then send an HTTP POST directly to the app's webhook endpoint with the identical body and HMAC but a different `x-shopify-shop-domain` header value. `HmacValidator.validate` still returns `true` because the header is never part of `to_signable_string`, and `Registry.process` forwards `request.shop` (the forged value) to the handler unchanged. No other guard in the gem intervenes: there is no session/shop lookup performed by the gem before calling the handler, and `ShopValidator`/`Context.setup?` are unrelated OAuth-path checks that this code path never calls.

### Impact Explanation
This lets an attacker cause a webhook handler to execute with an arbitrary, attacker-chosen `shop` value while still passing HMAC verification, i.e. the handler receives data it will treat as belonging to `shop_victim` even though the cryptographic proof only establishes `shop_attacker`'s content. Whether this becomes a full cross-tenant compromise depends entirely on how the host app's `WebhookHandler#handle` uses `data.shop` — this gem's own docs explicitly tell integrators to use `data.shop` as the trusted tenant key (`perform_later(topic: data.topic, shop_domain: data.shop, ...)`), so a host app following the documented pattern will index/write data under the forged shop domain. Repeatable against any victim domain the attacker chooses, for every topic the app has registered, at will and indefinitely (the same captured body/HMAC pair can be replayed many times).

### Likelihood Explanation
Preconditions are trivial for an unprivileged attacker: install the target app on a free development store, wait for/trigger one real webhook delivery, then replay body+HMAC directly to the app's public webhook endpoint with a swapped `x-shopify-shop-domain` header. No secrets are needed. The only requirement is that the host app trust `request.shop`/`WebhookMetadata#shop` for tenant-scoped writes/reads, which is exactly the pattern this gem's own documentation recommends.

### Recommendation
Bind the shop identity into the verified signature space, or independently authenticate `request.shop` before handing it to handlers. Concretely:
- Change `Request#to_signable_string` to include the shop domain (and/or topic/webhook id) alongside `@raw_body` so a captured signature cannot be replayed under a different domain, or
- Have `Registry.process` cross-validate `request.shop` against a known/installed-shop store (e.g. the app's session storage) before constructing `WebhookMetadata`, rejecting webhooks for shops that have no matching installation record, and
- Document clearly that `data.shop` must never be trusted as tenant-authenticated without such a cross-check, since the current HMAC only proves body authenticity, not shop binding.

### Proof of Concept
```ruby
# test/webhooks/registry_test.rb (new test)
def test_hmac_does_not_bind_shop_domain
  raw_body = "{}"
  secret = "shared_secret"
  ShopifyAPI::Context.setup(api_key: "key", api_secret_key: secret, host_name: "host",
    scope: "scope", is_private: false, is_embedded: true, api_version: "unstable")

  hmac = OpenSSL::HMAC.hexdigest(OpenSSL::Digest.new("sha256"), secret, raw_body)
  hmac_header = Base64.encode64(Digest.hexdecode(hmac))

  attacker_request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: {
    "shopify-topic" => "orders/create",
    "shopify-hmac-sha256" => hmac_header,
    "shopify-shop-domain" => "attacker.myshopify.com",
  })
  victim_request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: {
    "shopify-topic" => "orders/create",
    "shopify-hmac-sha256" => hmac_header,       # identical signature
    "shopify-shop-domain" => "victim.myshopify.com", # forged domain
  })

  handler = Minitest::Mock.new
  handler.expect(:handle, nil) do |data:|
    data.shop == "victim.myshopify.com"
  end
  ShopifyAPI::Webhooks::Registry.add_registration(topic: "orders/create", delivery_method: :http,
    path: "cb", handler: handler)

  assert ShopifyAPI::Utils::HmacValidator.validate(attacker_request)
  assert ShopifyAPI::Utils::HmacValidator.validate(victim_request) # same signature validates for forged shop

  ShopifyAPI::Webhooks::Registry.process(victim_request)
  handler.verify # handler.handle invoked with shop == "victim.myshopify.com" despite signature only proving attacker's body
end
```
Both `Request` objects assert `to_signable_string`/`hmac` equal, but `shop` diverges — proving the HMAC never bound the two together, and `Registry.process` forwards the forged value to the handler.

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
