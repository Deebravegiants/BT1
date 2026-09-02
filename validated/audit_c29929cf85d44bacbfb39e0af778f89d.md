Based on my investigation, there is a valid analog: the webhook `Request` class computes its HMAC over the raw body only, while the `shop` (and `topic`, `webhook_id`, `api_version`) fields are read directly from unauthenticated HTTP headers and passed through to the app's webhook handler as "verified" data.

### Title
Webhook `shop` identity is not bound by the HMAC, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` validates a webhook's authenticity using `Utils::HmacValidator`, which only signs/verifies the raw request body. The `shop` field, which the gem hands to the host application as the trusted tenant identifier, is taken straight from the `X-Shopify-Shop-Domain` header and is never included in the HMAC computation.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) . `HmacValidator.validate` computes and compares the signature purely against that signable string: [2](#0-1) . Meanwhile, `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are read directly, unauthenticated, from HTTP headers: [3](#0-2) .

`Registry.process` only checks that the HMAC is valid, then forwards `request.shop` (never verified) to the app's registered handler as the tenant identity for the webhook event: [4](#0-3) .

Because a Shopify app's `client_secret` (used to sign webhook payloads) is a single value shared across every shop that installs the app — not a per-shop secret — the HMAC only proves "this body was signed by Shopify for *some* installation of this app," not "this body/shop pairing is legitimate." The equality that should hold is:
`shop_header == shop_that_the_HMAC-signed_body_was_actually_delivered_for`
but the gem never enforces this; it only checks `HMAC(body) == HMAC(body, secret)`.

### Impact Explanation
An attacker who legitimately installs the target app on their own store receives real webhook deliveries with valid HMACs (signed with the app's shared `client_secret`). By capturing one such delivery and replaying it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header rewritten to a victim shop's domain, the request still passes `Utils::HmacValidator.validate` (since the body and HMAC are untouched), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the event is `shop: <victim-shop>`. Any host application that uses this `shop` value to key data writes, cache invalidation, order/customer sync, or session lookups will process attacker-supplied data under the victim's tenant — a cross-tenant data integrity/confidentiality break, without needing the app's `client_secret`, an access token, or any credential belonging to the victim.

### Likelihood Explanation
Exploitation requires only that the attacker be a legitimate (even free-tier) installer of the target app — no special privileges, leaked secrets, or victim-side action are required. Capturing and replaying one's own webhook payload with a modified header is straightforward for any developer with basic HTTP tooling, since webhook headers are set outside the signed payload by design.

### Recommendation
Bind the delivered `shop` (and ideally `topic`) into the value verified by the HMAC, or otherwise cryptographically tie them to the signed body — e.g., include the shop domain in the signable string, or require the consuming application to independently confirm that `shop` corresponds to a session/store known to actually be subscribed to that specific webhook topic before trusting `WebhookMetadata#shop`. At minimum, document prominently that `request.shop` is unauthenticated header data and must not be trusted as a tenant identity boundary without additional verification (e.g., cross-checking against the app's installed-shop records).

### Proof of Concept
1. Install the target Shopify app on attacker-controlled store `attacker.myshopify.com`.
2. Wait for (or trigger) a legitimate webhook delivery, e.g. `orders/create`, with body `B` and header `X-Shopify-Hmac-Sha256: H` where `H = HMAC-SHA256(client_secret, B)`.
3. Replay the same `B` and `H` to the app's webhook endpoint, but replace `X-Shopify-Shop-Domain: attacker.myshopify.com` with `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` succeeds because it only checks `B` and `H`. `Registry.process` in `lib/shopify_api/webhooks/registry.rb` dispatches to the handler with `shop: "victim.myshopify.com"`, and the host application processes attacker data as if it belonged to the victim shop.

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
