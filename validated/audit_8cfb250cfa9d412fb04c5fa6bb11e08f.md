This confirms the root cause precisely: `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from HTTP headers that are never included in the HMAC-covered bytes [2](#0-1) . `HmacValidator.validate` only checks `verifiable_query.hmac` against `to_signable_string` (the raw body) [3](#0-2) , and `Registry.process` trusts `request.shop` for tenant dispatch immediately after that check passes [4](#0-3) . The documented handler contract explicitly treats `data.shop` as the trusted per-tenant identifier for the app to act on [5](#0-4) .

### Title
Webhook shop-domain header is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw body only, while the `shop` (and `topic`/`webhook_id`/`api_version`) values used by the app are taken from unsigned HTTP headers. An unprivileged attacker who can submit HTTP requests to the app's public webhook endpoint (which by design accepts unauthenticated inbound POSTs from "Shopify") can attach a valid `hmac-sha256` value for any body they control paired with an arbitrary `shop-domain` header, and `Registry.process` will treat the payload as authentic for that arbitrary shop.

### Finding Description
The binding the app relies on is: `hmac` is valid ⇒ `shop` header is the true origin shop. In reality:
- `HmacValidator.validate_signature` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to `verifiable_query.hmac` [3](#0-2) .
- `Request#to_signable_string` returns only `@raw_body` — none of the Shopify-supplied headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) are part of the signed content [1](#0-0) .
- `Request#shop`, `#topic`, `#webhook_id` are all read directly from attacker-controllable headers with no cryptographic binding to the HMAC [2](#0-1) .
- `Registry.process` validates only the HMAC, then immediately forwards `request.shop` to the handler as the tenant identity: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))` [4](#0-3) .

Because the HMAC for a given webhook body is computed with the merchant's `client_secret`/`api_secret_key` and can be observed by anyone who receives (or is the recipient of) any single legitimate webhook delivery with that exact body — and many webhook topics carry generic/empty or shop-independent bodies (illustrated by the test using body `"{}"` and still succeeding validation) — an attacker who has legitimately received one webhook payload for their own shop can replay the identical `raw_body`+`hmac-sha256` value to the same endpoint while swapping only the `shop-domain` header to a victim shop. The gem's own verification path accepts this: `Utils::HmacValidator.validate(request)` returns true (body and HMAC are unchanged and consistent), yet `request.shop` now claims to be the victim shop [6](#0-5) . Test fixtures confirm the HMAC is computed purely from the body regardless of headers/shop values used [7](#0-6) .

### Impact Explanation
This breaks the tenant-isolation boundary the gem is supposed to enforce for webhook processing: an app built on this gem's documented `Registry.process` / `WebhookHandler` contract will dispatch webhook data under an attacker-chosen `shop` value despite HMAC validation "passing," because the HMAC never actually authenticates the shop-domain claim. This is a cross-tenant confusion vector — depending on the host app's use of `data.shop` (e.g., looking up the shop's stored session/access token to act on the webhook, or writing data keyed by shop), this could result in actions being taken against, or data attributed to, the wrong merchant.

### Likelihood Explanation
Requires only an unprivileged internet user able to POST to the app's public webhook endpoint with a body+HMAC pair they've observed (e.g., from a shop they themselves control receiving webhooks, since HMAC only depends on body content and the shared secret is per-app not per-shop — any shop installed on the same app shares the same `api_secret_key`). No access token, `api_secret_key`, or privileged credentials are needed beyond normal use of the app as an installed merchant.

### Recommendation
Include the `shop-domain` (and ideally `topic`, `webhook-id`) header values in the HMAC-signable content, or otherwise cryptographically bind the shop claim to the payload before trusting `request.shop` for tenant-scoped processing. At minimum, document that `to_signable_string` in `Request` does not cover headers and instruct integrators to cross-check `request.shop` against an expected/authorized shop set rather than trusting it implicitly.

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com` and `victim-shop.myshopify.com` (same `api_secret_key` per app).
2. Attacker's own shop receives a legitimate webhook, e.g. `orders/create` with raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid signature of `B`) and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker POSTs to the app's webhook endpoint with the same raw body `B`, same `X-Shopify-Hmac-Sha256: H`, but `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `to_signable_string` (= `B` only) and matches `H` — validation passes [6](#0-5) .
5. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, i.e., attacker-controlled body processed as though it originated from the victim shop [8](#0-7) .

### Citations

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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```

**File:** test/webhooks/registry_test.rb (L16-30)
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

        @webhook_request = ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: @headers)
```
