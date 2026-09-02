## Title
Webhook `shop` (and `topic`/`webhook_id`) header is trusted by the handler but not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating only the HMAC over the raw request body, then hands the caller-supplied `shop-domain` header straight to the app's handler as the tenant identifier. The HMAC never binds the `shop`, `topic`, or `webhook-id` headers to the signed payload, so a party who has legitimately received one valid `(body, hmac)` pair from Shopify (e.g. via their own app installation) can resend that exact pair to the app's webhook endpoint with an arbitrary `shop-domain` header and still pass validation.

### Finding Description
`Webhooks::Request#to_signable_string` only returns the raw body: [1](#0-0) 

while `shop`, `topic`, and `webhook_id` are read directly from HTTP headers with no cryptographic tie to the signed content: [2](#0-1) 

`Utils::HmacValidator.validate` computes/compares the signature purely against `to_signable_string` (the body): [3](#0-2) 

`Registry.process` then passes the unverified `request.shop` straight into the data given to the app's handler: [4](#0-3) 

The identity binding that should hold is:
`shop authenticated by HMAC == shop delivered to the handler`

but the actual binding enforced by the code is only:
`body authenticated by HMAC == body delivered to the handler`

The test suite explicitly demonstrates that the HMAC is computed from the body alone (`"{}"`) independent of whatever `shop-domain`/`topic`/`webhook-id` values are set in headers: [5](#0-4) 

### Impact Explanation
Because the `shop` field is not covered by the signature, a `(raw_body, hmac)` pair that Shopify legitimately generated and delivered for one shop's event remains a valid `(body, hmac)` pair when replayed with a different `shop-domain` header. Any actor capable of receiving one authentic webhook for the app (for instance, by installing the app on a shop they control) can capture that exact `body` + `x-shopify-hmac-sha256` value and resubmit it to the app's public webhook endpoint with the `shop-domain` header set to an arbitrary victim shop. `HmacValidator.validate` will still return `true`, and `Registry.process` will invoke the app's handler with `WebhookMetadata.shop` set to the attacker-chosen victim domain and `body` set to attacker-influenced content, since the attacker fully controls what events/data occur on their own shop that will end up in that signed body. If the host application uses `data.shop` to select the tenant record to update (a common pattern), this allows cross-tenant data injection/corruption without possessing the app's `client_secret` — matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires the attacker to be able to install the app (or otherwise trigger a genuine webhook delivery) on a shop they control, which is realistic for any unprivileged Shopify merchant/developer account, and then send a raw HTTP POST with the captured body/HMAC/spoofed header to the app's public webhook endpoint. No access to the app's `client_secret`, access tokens, or TLS interception is needed. The only variable outside attacker control is the specific JSON content Shopify generates for the triggered event, but that is often attacker-influenceable (e.g. `orders/create`, `customers/create` payload fields set by the attacker themselves in their own store).

### Recommendation
Bind the header-derived identifiers into the signed content that `HmacValidator` verifies (or otherwise cryptographically tie `shop`, `topic`, and `webhook_id` to the HMAC), and/or require the host application to cross-check `request.shop` against the shop expected for the given webhook subscription/session before acting on the payload. At minimum, document prominently that `shop`, `topic`, and `webhook_id` headers are unauthenticated and must not be trusted as tenant identifiers without an independent check.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a webhook event (e.g., creates an order with attacker-chosen fields) so Shopify delivers a webhook POST to the app's registered endpoint with a valid `x-shopify-hmac-sha256` computed over that JSON body.
2. Attacker captures the raw body and `x-shopify-hmac-sha256` value from that legitimate delivery.
3. Attacker sends a new POST request to the same app webhook endpoint with the identical raw body and `x-shopify-hmac-sha256` header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and desired `x-shopify-topic`/`x-shopify-webhook-id`).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because only the body is checked (`lib/shopify_api/utils/hmac_validator.rb:26-31`, `lib/shopify_api/webhooks/request.rb:35-38`).
5. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: attacker-controlled JSON, ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), and any host-app logic keyed on `data.shop` operates on the victim tenant using attacker-supplied data.

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

**File:** test/webhooks/registry_test.rb (L16-33)
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
        @session = ShopifyAPI::Auth::Session.new(shop: ShopifyAPI::Context.host_name, access_token: "access_token")
        @url = "#{ShopifyAPI::Context.host}/admin/api/#{ShopifyAPI::Context.api_version}/graphql.json"
      end
```
