### Title
Webhook shop identity spoofing due to HMAC not covering the `shop-domain` header - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, `api_version`, and `webhook_id` directly from unauthenticated HTTP headers, while the HMAC signature validated by `HmacValidator` only covers the raw request body. This breaks the identity binding `signed(shop) == acted_on(shop)`: the signature proves the body's integrity but not which shop the webhook is about, letting an app-installing attacker replay a signed payload from their own shop while claiming to be a different (victim) shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header without any cryptographic binding to that value [2](#0-1) .

`Registry.process` only checks `Utils::HmacValidator.validate(request)` against the body, then immediately trusts `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` to build the `WebhookMetadata` handed to the app's handler [3](#0-2) .

`HmacValidator.validate_signature` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to the received `hmac` header [4](#0-3) . Because `to_signable_string` for webhooks is only the raw JSON body, the signature is a function purely of `(api_secret_key, body)` — it is identical for every shop and every topic that happens to send that same body. The shop identity is asserted out-of-band via a plain, unsigned header.

Since the same `api_secret_key` is shared across all shops that install the app, any merchant who has legitimately installed the app can:
1. Trigger (or receive) a real webhook delivery to their own shop, capturing a valid `(raw_body, x-shopify-hmac-sha256)` pair for a topic of their choosing (e.g. `app/uninstalled`, `customers/data_request`, `shop/redact`, or any topic the app subscribes to with attacker-influenced body content).
2. Replay that exact body and HMAC to the app's public webhook endpoint, but substitute the `x-shopify-shop-domain` header with a victim shop's domain.
3. `HmacValidator.validate` still passes (the body/HMAC pair is valid), yet `Registry.process` builds `WebhookMetadata` with `shop: <victim shop>` [5](#0-4) .

The app's registered handler (implementing `WebhookHandler#handle`) receives this metadata and will act on the victim shop's tenant data using attacker-supplied body content — this is a cross-tenant identity binding break: `shop asserted by header != shop covered by HMAC`.

### Impact Explanation
This falls under the "cross-tenant access" Critical class: an attacker (any merchant with an installed instance of the app, i.e., an "unprivileged" party with respect to other tenants) can impersonate another shop's webhook events. Depending on how the host app's `WebhookHandler` implementation uses `data.shop` (e.g., to look up `Session`/access tokens, trigger uninstall/data-deletion flows, or write to per-shop storage), this can lead to unauthorized cross-tenant data manipulation, forged "app/uninstalled" or GDPR mandatory webhooks against a victim shop, or corruption of a victim shop's stored state — without ever needing the victim's credentials or the app's `api_secret_key`.

### Likelihood Explanation
Requires only that the attacker be a legitimate merchant able to install the app (to generate at least one valid signed webhook body/HMAC pair) and knowledge of the target's `myshopify.com` domain (public information). No secret material or session hijacking is needed. This is fully reachable through the gem's documented webhook-processing API (`Registry.process` / `Request.new`) as shipped, not a misuse of it.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the signed material, or otherwise cryptographically tie the HMAC to the asserted shop domain, e.g. by including the `shop-domain` header value in `to_signable_string`, or by requiring the caller to independently verify that `request.shop` matches an expected/registered shop for the given `access_token`/session before trusting the payload. At minimum, document prominently that `Registry.process` does not authenticate the `shop` field and that host applications must not use it to select tenant context without additional verification.

### Proof of Concept
```ruby
# Attacker installs the app on their own shop "attacker.myshopify.com"
# and receives (or triggers) a legitimate webhook, capturing:
raw_body = '{"id": 1, "malicious": "payload"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body)

# Attacker then POSTs to the app's webhook endpoint, replaying the same
# signed body but claiming to be the victim shop:
headers = {
  "x-shopify-topic" => "app/uninstalled",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),   # still valid! HMAC never covered "shop"
  "x-shopify-shop-domain" => "victim-shop.myshopify.com",
  "x-shopify-webhook-id" => "attacker-chosen-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) returns true (body/HMAC match),
#    handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...))
#    is invoked as if the event genuinely originated from victim-shop.
```

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
